from flask import Flask, render_template, request, jsonify
from backend.retrieval import get_ingredient_context
from backend.gpt import generate_meal_idea, generate_image_prompt, generate_script
from backend.audio import generate_audio
from backend.image import generate_image
import base64


# Flask Setup
app = Flask(__name__)


# Routes

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api", methods=["POST"])
def api():
    try:
        user_input = request.json.get("message", "")

        # Step 1: Retrieve relevant ingredient facts from knowledge base
        ingredient_context = get_ingredient_context(user_input)

        # Step 2: Generate recipe text using GPT-4 and ingredient context
        recipe = generate_meal_idea(user_input, ingredient_context)

        # Step 3: Create DALL-E prompt and generate image
        image_prompt = generate_image_prompt(recipe)
        image_url = generate_image(image_prompt)

        # Step 4: Generate a short voiceover script and audio
        voice_script = generate_script(recipe)
        audio_base64 = generate_audio(voice_script)

        return jsonify({
            "text": recipe,
            "image_url": image_url,
            "audio_base64": audio_base64
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)