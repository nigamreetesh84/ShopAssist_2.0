import json
import re
import pandas as pd
from openai import OpenAI
import time

MODEL = "gpt-3.5-turbo"                   
CLIENT = OpenAI(api_key=open('OPENAI_API_Key.txt').read().strip())

LAPTOP_CSV = "updated_laptop.csv"

# ---------- Utility helpers ----------
def truncate_conversation(messages, max_turns=4):
    """Keep only the last N turns + system prompt to reduce tokens."""
    if not isinstance(messages, list) or len(messages) <= max_turns:
        return messages
    return [messages[0]] + messages[-max_turns:]

def parse_budget(budget_raw: str) -> int:
    """Extract digits from strings like '90,000 INR' or '90000'."""
    if budget_raw is None:
        return 0
    s = re.sub(r"[^\d]", "", str(budget_raw))
    return int(s) if s else 0

def load_laptops():
    """Load laptop CSV as dataframe."""
    df = pd.read_csv(LAPTOP_CSV)
    if "Price" in df.columns:
        df["Price"] = df["Price"].astype(str).str.replace(",", "").astype(int)
    return df

def summarize_recommendations(recs: list) -> list:
    """Summarizes laptop recommendations for token efficiency."""
    summarized = []
    for r in recs:
        summary = {
            "name": r.get("Model Name", ""),
            "price": r.get("Price", ""),
            "features": r.get("Special Features", "")[:100] + "..."
        }
        summarized.append(summary)
    return summarized

def initialize_conversation():
    """Sets up the initial system prompt for the conversation."""
    return [{
        "role": "system",
        "content": "You are a helpful and friendly assistant named ShopAssist, a laptop recommendation chatbot. Use the functions provided to answer questions about laptops. Greet the user and tell them you can help find laptops based on their needs, such as budget, usage (e.g., gaming, work, student), and specific features."
    }]

def get_laptop_recommendations(budget, gpu, display, portability, multitasking, speed):
    """
    Finds and recommends laptops from a dataset based on a user's criteria.
    Args:
        budget (str): The maximum budget for the laptop.
        gpu (str): The priority for GPU performance ('high', 'medium', 'low').
        display (str): The priority for display quality ('high', 'medium', 'low').
        portability (str): The priority for portability ('high', 'medium', 'low').
        multitasking (str): The priority for multitasking ('high', 'medium', 'low').
        speed (str): The priority for general speed ('high', 'medium', 'low').
    Returns:
        dict: A dictionary containing a list of recommended laptops.
    """
    try:
        df = load_laptops()
        df["Score"] = 0
        parsed_budget = parse_budget(budget)

        if parsed_budget > 0:
            df = df[df["Price"] <= parsed_budget]
        
        if gpu == 'high': df['Score'] += (df['laptop_feature'].str.contains("'GPU intensity': 'high'").astype(int) * 3)
        if display == 'high': df['Score'] += (df['laptop_feature'].str.contains("'Display quality': 'high'").astype(int) * 3)
        if portability == 'high': df['Score'] += (df['laptop_feature'].str.contains("'Portability': 'high'").astype(int) * 3)
        if multitasking == 'high': df['Score'] += (df['laptop_feature'].str.contains("'Multitasking': 'high'").astype(int) * 3)
        if speed == 'high': df['Score'] += (df['laptop_feature'].str.contains("'Processing speed': 'high'").astype(int) * 3)

        df = df.sort_values(by="Score", ascending=False)
        recommendations = df.head(3).to_dict('records')

        if not recommendations:
            return {"recommendations": [], "message": "No laptops found for your criteria."}
        
        return {"recommendations": recommendations}
    except Exception as e:
        return {"error": str(e), "recommendations": []}

FUNCTIONS = [
    {
        "name": "get_laptop_recommendations",
        "description": "Recommends laptops based on user criteria like budget, usage, and priority for certain features.",
        "parameters": {
            "type": "object",
            "properties": {
                "budget": {
                    "type": "string", 
                    "description": "The maximum budget. Defaults to a reasonable value if not specified. E.g., '60000'."
                },
                "gpu": {
                    "type": "string",
                    "enum": ["high", "medium", "low"],
                    "description": "GPU priority. Use 'high' for gaming/video editing, 'medium' for general use, and 'low' for basic tasks.",
                },
                "display": {
                    "type": "string",
                    "enum": ["high", "medium", "low"],
                    "description": "Display quality priority. Use 'high' for content creation/movies, 'medium' for general use, and 'low' for basic tasks.",
                },
                "portability": {
                    "type": "string",
                    "enum": ["high", "medium", "low"],
                    "description": "Portability priority. Use 'high' for frequent travel, 'medium' for occasional travel, and 'low' for a stationary setup.",
                },
                "multitasking": {
                    "type": "string",
                    "enum": ["high", "medium", "low"],
                    "description": "Multitasking ability priority. Use 'high' for running many apps, 'medium' for general use, and 'low' for basic web browsing.",
                },
                "speed": {
                    "type": "string",
                    "enum": ["high", "medium", "low"],
                    "description": "General speed priority. Use 'high' for intensive tasks, 'medium' for general use, and 'low' for basic office work.",
                },
            },
            "required": [],
        },
    }
]

def chat_with_functions(conversation):
    """Core function to manage the chat flow with function calling."""
    conv = truncate_conversation(conversation)

    try:
        resp = CLIENT.chat.completions.create(
            model=MODEL,
            messages=conv,
            functions=FUNCTIONS,
            function_call="auto"
        )
    except Exception as e:
        return {"error": f"OpenAI API error during initial call: {e}"}

    message = resp.choices[0].message
    
    if message.function_call:
        fname = message.function_call.name
        try:
            fargs = json.loads(message.function_call.arguments.replace("'", '"'))
        except json.JSONDecodeError as e:
            return {"error": f"JSON decoding error in function arguments: {e}"}

        if fname == "get_laptop_recommendations":
            result = get_laptop_recommendations(
                budget=fargs.get("budget", ""),
                gpu=fargs.get("gpu", ""),
                display=fargs.get("display", ""),
                portability=fargs.get("portability", ""),
                multitasking=fargs.get("multitasking", ""),
                speed=fargs.get("speed", ""),
            )
        else:
            result = {"error": f"Unknown function {fname}"}

        if "recommendations" in result and result.get("recommendations"):
            # If recommendations are found, summarize them and send them back
            result["recommendations"] = summarize_recommendations(result["recommendations"])
        else:
            # If no recommendations are found, try again with relaxed criteria
            if fargs.get("gpu") == 'high': fargs["gpu"] = 'medium'
            if fargs.get("multitasking") == 'high': fargs["multitasking"] = 'medium'
            if fargs.get("speed") == 'high': fargs["speed"] = 'medium'
            
            # Recalculate with relaxed criteria
            result = get_laptop_recommendations(
                budget=fargs.get("budget", ""),
                gpu=fargs.get("gpu", ""),
                display=fargs.get("display", ""),
                portability=fargs.get("portability", ""),
                multitasking=fargs.get("multitasking", ""),
                speed=fargs.get("speed", ""),
            )
            # Summarize the new recommendations if any were found
            if "recommendations" in result and result.get("recommendations"):
                result["recommendations"] = summarize_recommendations(result["recommendations"])

        conversation.append(message)
        conversation.append({
            "role": "function",
            "name": fname,
            "content": json.dumps(result)
        })

        try:
            final_resp = CLIENT.chat.completions.create(
                model=MODEL,
                messages=conversation,
                max_completion_tokens=100
            )
            assistant_text = final_resp.choices[0].message.content
            return {"assistant_text": assistant_text, "structured": result}
        except Exception as e:
            return {"error": f"OpenAI API error during finalization: {e}", "structured": result}

    return {"assistant_text": message.content}