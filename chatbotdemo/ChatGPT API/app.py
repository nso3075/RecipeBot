from flask import Flask, render_template, request, jsonify
from backend.retrieval import get_ingredient_context
from backend.gpt import generate_meal_idea, generate_chat_response, generate_image_prompt, generate_script
from backend.audio import generate_audio
from backend.image import generate_image
from dotenv import load_dotenv
import base64
import traceback

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Persistent conversation state
conversation_mode = "recipe"
conversation_history = []
saved_ingredients = []

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api", methods=["POST"])
def api():
    global conversation_mode, conversation_history, saved_ingredients

    try:
        user_input = request.json.get("message", "").strip()
        print("[INPUT]", user_input)

        # --- Reset ---
        if user_input.lower() in ["reset", "start over", "new recipe"]:
            conversation_history = []
            conversation_mode = "recipe"
            saved_ingredients = []
            print("[MODE] Reset to recipe mode")
            return jsonify({
                "text": "🔄 Reset! Please type:\n\n1️⃣ for Recipe Mode (create meals)\n2️⃣ for Chat Mode (ask about tips or swaps)",
                "image_url": "", "audio_base64": ""
            })

        # --- Mode Switching ---
        if user_input == "1":
            conversation_mode = "recipe"
            print("[MODE] Switched to recipe mode")
            return jsonify({"text": "✅ Recipe Mode activated! Send ingredients to get started.", "image_url": "", "audio_base64": ""})
        if user_input == "2":
            conversation_mode = "chat"
            print("[MODE] Switched to chat mode")
            return jsonify({"text": "💬 Chat Mode activated! Ask about substitutions, flavors, or cooking advice.", "image_url": "", "audio_base64": ""})

        # --- Recipe Mode ---
        if conversation_mode == "recipe":
            saved_ingredients = [i.strip().lower() for i in user_input.split(",") if i.strip()]
            print("[INGREDIENTS]", saved_ingredients)

            # Get context for RAG
            ingredient_context = get_ingredient_context(user_input)
            print("[CONTEXT]", ingredient_context)

            # Generate recipe
            try:
                print("[DEBUG] Generating recipe...")
                recipe = generate_meal_idea(user_input, ingredient_context)
                print("[DEBUG] Recipe generated")
            except Exception as e:
                print("[ERROR] Failed to generate recipe:", e)
                recipe = "<p>⚠️ Sorry, I couldn't generate a recipe.</p>"

            # Generate image
            try:
                image_prompt = generate_image_prompt(recipe)
                image_url = generate_image(image_prompt)
                print("[DEBUG] Image generated:", image_url)
            except Exception as e:
                print("[WARNING] Image generation failed:", e)
                image_url = ""

            # Generate audio
            try:
                voice_script = generate_script(recipe)
                audio_base64 = generate_audio(voice_script)
                print("[DEBUG] Audio generated")
            except Exception as e:
                print("[WARNING] Audio generation failed:", e)
                audio_base64 = ""

            return jsonify({
                "text": recipe + "<p>💬 Want to chat? Type <strong>2</strong> for Chat Mode.</p>",
                "image_url": image_url,
                "audio_base64": audio_base64
            })

        # --- Chat Mode ---
        else:
            try:
                print("[DEBUG] Generating chat response...")
                chat_response = generate_chat_response(user_input, saved_ingredients)
                print("[DEBUG] Chat response generated")
            except Exception as e:
                print("[ERROR] Chat generation failed:", e)
                chat_response = "<p>⚠️ Sorry, I couldn't answer that.</p>"

            try:
                audio_base64 = generate_audio(chat_response)
            except Exception as e:
                print("[WARNING] Chat audio generation failed:", e)
                audio_base64 = ""

            return jsonify({
                "text": chat_response + "<p>🥘 Want a new recipe? Type <strong>1</strong> for Recipe Mode.</p>",
                "image_url": "",
                "audio_base64": audio_base64
            })

    except Exception as e:
        print("[SERVER ERROR]", str(e))
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
