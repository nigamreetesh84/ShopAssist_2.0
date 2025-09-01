from flask import Flask, render_template, request, redirect, url_for
from functions import chat_with_functions, truncate_conversation, initialize_conversation as init_conv, FUNCTIONS

app = Flask(__name__)

conversation = init_conv()
conversation_history = []
DISPLAY_LIMIT = 800  # Limit for displayed text

@app.route("/", methods=["GET"])
def index():
    """Renders the main chat interface."""
    return render_template("index.html", name_xyz=conversation_history)

@app.route("/end_conv", methods=["POST", "GET"])
def end_conv():
    """Resets the conversation to start a new chat session."""
    global conversation, conversation_history
    conversation = init_conv()
    conversation_history = []
    g = chat_with_functions(conversation)
    if "assistant_text" in g:
        conversation.append({"role": "assistant", "content": g["assistant_text"]})
        conversation_history.append({"bot": g["assistant_text"]})
    return redirect(url_for("index"))

@app.route("/invite", methods=["POST"])
def invite():
    """Handles user input, interacts with the chat function, and updates the conversation."""
    global conversation, conversation_history
    user_input = request.form.get("user_input_message", "")[:DISPLAY_LIMIT]

    conversation.append({"role": "user", "content": user_input})
    conversation_history.append({"user": user_input})
    print(f"User Input: {user_input}")
    print(f"Conversation so far: {conversation}")
    try:
        response_data = chat_with_functions(conversation)
    except Exception as e:
        print(f"Error during chat_with_functions: {e}")
        response_data = {"assistant_text": f"An error occurred: {e}"}
    print(f"Response Data: {response_data}")
    assistant_text = response_data.get("assistant_text")
    structured = response_data.get("structured")

    if assistant_text:
        short_text = assistant_text if len(assistant_text) <= DISPLAY_LIMIT else assistant_text[:DISPLAY_LIMIT] + "..."
        conversation.append({"role": "assistant", "content": short_text})
        conversation_history.append({"bot": short_text})
    else:
        fallback = "I couldn't generate a response right now."
        conversation.append({"role": "assistant", "content": fallback})
        conversation_history.append({"bot": fallback})

    if structured and isinstance(structured, dict):
        recs = structured.get("recommendations", [])
        if recs:
            summary_lines = []
            for idx, r in enumerate(recs, 1):
                # Now we use the summarized fields
                name = r.get("name", "")
                price = r.get("price", "")
                features = r.get("features", "")
                line = f"{idx}. {name} — Price: {price} — Features: {features}"
                summary_lines.append(line)
            summary = "Top recommendations:\n" + "\n".join(summary_lines)
            conversation_history.append({"bot": summary})

    return redirect(url_for("index"))

if __name__ == "__main__":
    """Starting the Flask application and initializes the conversation."""
    data = chat_with_functions(conversation)
    if "assistant_text" in data:
        conversation.append({"role": "assistant", "content": data["assistant_text"]})
        conversation_history.append({"bot": data["assistant_text"]})

    app.run(debug=True, host="0.0.0.0")
