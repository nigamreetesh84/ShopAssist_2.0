
# ShopAssist 2.0

ShopAssist 2.0 is an AI-powered chatbot that helps users find the best laptops based on their budget, preferences, and usage.  
This version enhances the original ShopAssist by integrating **OpenAI's Function Calling API**, making conversations more natural, structured, and efficient.

---

## 🚀 Features

- Laptop recommendations based on budget and feature priorities (GPU, display, portability, multitasking, speed).  
- **Function Calling API** integration – the assistant automatically decides when to call functions.  
- Summarized recommendations for better readability.  
- Fallback mechanism: relaxes strict criteria if no results are found.  
- Flask-based web app with a simple chat interface (`index.html`).  
- Conversation history management with token efficiency.

---

## 📂 Project Structure

```
ShopAssist_2.0/
│
├── app.py                   # Flask app (routes, conversation state, UI)
├── functions.py             # AI logic, function calling, dataset handling
├── templates/
│   └── index.html           # Frontend chat interface
├── static/
│    ├── css/
│       └── styles.css           # Frontend styles  
├── updated_laptop.csv       # Dataset containing laptop details
│
├── requirements.txt         # Python dependencies
├── README.md                # Project documentation (this file)
└── ShopAssist_2.0_Project_Report.docx
    
```

---

## ⚙️ Installation

### 1. Clone the repository
```bash
git clone <your-repo-link>
cd ShopAssist_2.0
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Add OpenAI API Key
Create a file named `OPENAI_API_Key.txt` in the project root and paste your OpenAI API key inside.

---

## ▶️ Usage

Run the Flask app:

```bash
python app.py
```

Open your browser and navigate to:
```
http://127.0.0.1:5000/
```

Type queries like:
- *“Suggest a laptop under 70,000 INR for gaming.”*  
- *“Find me a lightweight laptop with good multitasking.”*  

The assistant will reply with both conversational text and structured recommendations.

---

## 📘 Code Overview

- **app.py**  
  - Manages Flask routes (`/`, `/invite`, `/end_conv`).  
  - Handles user input, conversation history, and rendering chat.  

- **functions.py**  
  - Contains helper functions for budget parsing, conversation trimming, dataset loading.  
  - Implements `get_laptop_recommendations`.  
  - Defines function schema (`FUNCTIONS`) for OpenAI’s function calling.  
  - Integrates OpenAI’s API in `chat_with_functions`.  

- **index.html**  
  - Template for the chat interface.  
  - Displays user queries, assistant responses, and recommendations.  

---

## 🛠 Challenges Faced

- Parsing JSON safely from function call arguments.  
- Managing conversation history while avoiding token overflow.  
- Ensuring fallback logic still felt natural to users.  
- Cleaning and aligning dataset features for accurate scoring.  

---

## 🎯 Lessons Learned

- Function Calling simplifies chatbot architecture – less manual parsing.  
- Summarization improves token efficiency and user readability.  
- Fallback logic improves user satisfaction.  
- Proper documentation and modular code make replication easier.  

---





