from flask import Flask, render_template, request, jsonify
from openai import OpenAI
from elevenlabs.client import ElevenLabs
import base64

app = Flask(__name__)

# --- API Keys Setup ---
OPENAI_API_KEY = "YOUR_OPENAI_API_KEY"
ELEVENLABS_API_KEY = "YOUR_ELEVENLABS_API_KEY"
VOICE_ID = "YOUR_ELEVENLABS_VOICE_ID"

openai_client = OpenAI(api_key=OPENAI_API_KEY)
voice_client = ElevenLabs(api_key=ELEVENLABS_API_KEY)

# --- System Message for GPT ---
# (Defines how GPT behaves across all conversations)
SYSTEM_MESSAGE = {
    "role": "system",
    "content": (
        "You are a focused, friendly, and concise food chatbot assisting college students with dorm-friendly meals. "
        "ONLY answer user questions directly based on what they specifically ask. "
        "Do NOT invent unrelated recipes, side ideas, or desserts unless asked. "
        "Format all responses using simple HTML (<p>, <h2>, <h3>, <ul>, <li>). "
        "Be creative only when necessary but always respect user intent first."
    )
}

# --- Global Variables ---
conversation_history = [SYSTEM_MESSAGE]  # Tracks the full conversation (for GPT context)
conversation_mode = "recipe"  # Either 'recipe' or 'chat'
MAX_HISTORY = 10  # Limit the number of conversation turns kept
recipe_pending = False  # Track if a recipe is currently pending after generation
last_recipe_text = ""  # Store last generated recipe (for image/audio)
saved_ingredients = []  # Stores user's last given ingredients list

# --- Routes ---
@app.route("/")
def index():
    # Load the frontend chat interface
    return render_template("index.html")

@app.route("/api", methods=["POST"])
def api():
    global conversation_history, recipe_pending, last_recipe_text, conversation_mode, saved_ingredients

    user_input = request.json.get("message", "").strip()

    try:
        # --- Handle Reset Commands ---
        if user_input.lower() in ["new recipe", "start over", "reset"]:
            conversation_history = [SYSTEM_MESSAGE]
            conversation_mode = "recipe"
            recipe_pending = False
            last_recipe_text = ""
            saved_ingredients = []
            return jsonify({
                "text": "🔄 Reset! Please type:\n\n1️⃣ for Recipe Mode (create meals)\n2️⃣ for Chat Mode (ask for advice, swaps, or tips).",
                "image_url": "",
                "audio_base64": ""
            })

        # --- Handle Switching Modes ---
        if user_input == "1":
            conversation_mode = "recipe"
            return jsonify({
                "text": "✅ You're now in Recipe Mode! Please send your list of ingredients to create a meal.",
                "image_url": "",
                "audio_base64": ""
            })

        if user_input == "2":
            conversation_mode = "chat"
            return jsonify({
                "text": "✅ You're now in Chat Mode! Feel free to ask about swaps, cooking tips, or suggestions.",
                "image_url": "",
                "audio_base64": ""
            })

        # --- Build GPT Prompt Based on Mode ---
        if conversation_mode == "recipe":
            # Save the latest list of ingredients
            saved_ingredients = [i.strip().lower() for i in user_input.split(",") if i.strip()]

            # Build prompt to generate a new recipe
            prompt = (
                "You are a friendly expert chef. "
                "Create a detailed, creative recipe using ONLY these ingredients: "
                f"{user_input}. "
                "Format using simple HTML: <h2>/<h3> for sections, <ul>/<li> for lists, <p> for paragraphs. Avoid Markdown."
            )

        elif conversation_mode == "chat":
            # Define keyword triggers for swap and flavor enhancement detection
            allergy_trigger_words = ["allergic", "substitute", "swap", "replace", "instead of"]
            flavor_boost_trigger_words = ["enhance", "better", "improve", "add flavor", "boost", "make better", "upgrade taste", "more flavorful"]

            user_lower = user_input.lower()

            # Try to detect if the user wants to swap a specific ingredient
            ingredient_to_swap = None
            for trigger in allergy_trigger_words:
                if trigger in user_lower:
                    words = user_lower.split()
                    try:
                        idx = words.index(trigger)
                        if idx + 1 < len(words):
                            ingredient_to_swap = words[idx + 1]
                    except ValueError:
                        pass

            # Fallback: match saved ingredients if user didn't mention clearly
            if not ingredient_to_swap and saved_ingredients:
                for ing in saved_ingredients:
                    if ing in user_lower:
                        ingredient_to_swap = ing
                        break

            # Detect if the user asked for flavor enhancement
            flavor_boost_request = any(word in user_lower for word in flavor_boost_trigger_words)

            # Build a specific prompt based on the type of question
            if ingredient_to_swap:
                prompt = (
                    f"You are a food advisor specializing in substitutions. "
                    f"The user needs a substitution for '{ingredient_to_swap}'. "
                    "Suggest 1–3 allergy-safe or accessible replacements. "
                    "Respond using simple <p> HTML only. Keep it short and clear."
                )
            elif flavor_boost_request and saved_ingredients:
                prompt = (
                    f"You are a food flavor expert. "
                    f"The user previously gave these ingredients: {', '.join(saved_ingredients)}. "
                    "Suggest 1–3 easy, dorm-friendly ingredients they could add to boost flavor or improve their dish. "
                    "Use simple <p> HTML tags. No extra explanations needed."
                )
            else:
                prompt = (
                    "You are a friendly food advisor for college students. "
                    "Try to assist the user with their food related inquiries as best you can. "
                    "Respond using simple HTML <p> formatting."
                )

        # --- Update Conversation History ---
        conversation_history.append({"role": "user", "content": prompt})
        if len(conversation_history) > MAX_HISTORY:
            conversation_history = [SYSTEM_MESSAGE] + conversation_history[-MAX_HISTORY:]

        # --- GPT API Call ---
        gpt_response = openai_client.chat.completions.create(
            model="gpt-4.1",
            messages=conversation_history
        )
        bot_reply = gpt_response.choices[0].message.content
        conversation_history.append({"role": "assistant", "content": bot_reply})

        # --- Handle Recipe Mode Special Features (Image + Audio) ---
        if conversation_mode == "recipe" and ("<h2>" in bot_reply or "<h3>" in bot_reply) and ("<ul>" in bot_reply):
            recipe_pending = True
            last_recipe_text = bot_reply

            # --- Generate DALL-E Image of the Dish ---
            image_prompt_response = openai_client.chat.completions.create(
                model="gpt-4.1",
                messages=[
                    SYSTEM_MESSAGE,
                    {"role": "user", "content": f"Describe a DALL-E prompt for the finished dish: {last_recipe_text}"}
                ]
            )
            image_prompt = image_prompt_response.choices[0].message.content

            image = openai_client.images.generate(
                model="dall-e-3",
                prompt=image_prompt,
                size="1024x1024",
                quality="standard",
                n=1,
            )
            image_url = image.data[0].url

            # --- Generate ElevenLabs Audio Reading the Recipe ---
            voice_script = f"Here's the recipe: {last_recipe_text}"
            audio = voice_client.text_to_speech.convert(
                voice_id=VOICE_ID,
                output_format="mp3_44100_128",
                text=voice_script,
                model_id="eleven_multilingual_v2",
            )
            audio_base64 = base64.b64encode(b"".join(audio)).decode("utf-8")

            # --- Return Full Recipe + Image + Audio ---
            follow_up = (
                "<p>🍽️ Did you like this recipe? "
                "I can suggest ingredient swaps, drink pairings, or meal improvements.</p>"
                "<p>💬 Want to ask about substitutions or flavor tips? Type <strong>2</strong> to enter Chat Mode!</p>"
            )

            return jsonify({
                "text": bot_reply + follow_up,
                "image_url": image_url,
                "audio_base64": audio_base64
            })

        else:
            # --- Return Chat-Only Response ---
            return jsonify({
                "text": bot_reply + (
                    "<p>💬 Want to create a full new meal? Type <strong>1</strong> to return to Recipe Mode!</p>"
                ),
                "image_url": "",
                "audio_base64": ""
            })

    except Exception as e:
        # --- If anything fails, return error info ---
        return jsonify({"error": str(e)}), 500

# --- App Runner ---
if __name__ == "__main__":
    app.run(debug=True)
