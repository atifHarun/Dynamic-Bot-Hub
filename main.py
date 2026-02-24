import os
import json
from flask import Flask, render_template, request, jsonify, abort
from openai import OpenAI

app = Flask(__name__)

# Initialize OpenAI client using the OPENAI_API_KEY environment variable
api_key = os.environ.get("OPENAI_API_KEY")
client = OpenAI(api_key=api_key) if api_key else None

# Directory where bot configurations are stored
CONFIG_DIR = "configs"

def get_bot_filename(bot_type):
    mapping = {
        "agriculture": "Agricultural Decision Optimizer.json",
        "hospital": "General Hospital Patient Navigator.json",
        "cookie": "Online Cookie Shop Customer Support Chatbot.json",
        "school": "School IT Helper.json",
        "hotel": "Voice-Activated Hotel In-Room Assistant.json"
    }
    return mapping.get(bot_type, f"{bot_type}.json")

def load_bot_config(bot_type):
    """Load the JSON configuration for the specified bot_type."""
    filename = get_bot_filename(bot_type)
    file_path = os.path.join(CONFIG_DIR, filename)
    if not os.path.exists(file_path):
        return None
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

@app.route("/")
def index():
    """Serve the directory page."""
    return render_template("index.html")

@app.route("/bot/<bot_type>")
def bot_page(bot_type):
    """Serve the webpage for the specific chatbot."""
    config = load_bot_config(bot_type)
    if not config:
        abort(404, description=f"Configuration for '{bot_type}' not found.")
    
    return render_template("bot.html", bot_type=bot_type, bot_name=config.get("name", "Chatbot"))

@app.route("/chat", methods=["POST"])
def chat():
    """Handle chat requests from the frontend."""
    data = request.json
    bot_type = data.get("botType")
    user_message = data.get("message")
    
    if not bot_type or not user_message:
        return jsonify({"error": "Missing botType or message"}), 400
        
    config = load_bot_config(bot_type)
    if not config:
        return jsonify({"error": f"Configuration for '{bot_type}' not found."}), 404
        
    # Construct the system prompt
    system_prompt = (
        f"You are a specialized assistant.\n\n"
        f"Configuration:\n{json.dumps(config, indent=2)}\n\n"
        f"Instructions:\n"
        f"- Stay within your primaryFunction.\n"
        f"- Respect constraints and escalation rules defined in the configuration.\n"
    )
    
    if not client:
        return jsonify({"error": "OPENAI_API_KEY environment variable is not set."}), 500

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ]
        )
        assistant_reply = response.choices[0].message.content
        return jsonify({"reply": assistant_reply})
    except Exception as e:
        return jsonify({"error": f"OpenAI request failed: {str(e)}"}), 500

if __name__ == "__main__":
    # Host on 0.0.0.0 and port 5000 to be accessible on Replit
    app.run(host="0.0.0.0", port=5000, debug=True)
