from flask import Flask, render_template, request, jsonify
from openai import OpenAI
from elevenlabs.client import ElevenLabs
import base64

# ------------------------------------------
# Flask App & API Client Setup
# ------------------------------------------

# Initialize Flask app
app = Flask(__name__)

# API Keys (replace with your own or use env vars for security)
OPENAI_API_KEY = "KEY"
ELEVENLABS_API_KEY = "KEY"
VOICE_ID = "KEY"  # Example ElevenLabs voice

# Initialize OpenAI & ElevenLabs clients
openai_client = OpenAI(api_key=OPENAI_API_KEY)
voice_client = ElevenLabs(api_key=ELEVENLABS_API_KEY)

# ------------------------------------------
# Routes
# ------------------------------------------

# Home route: serves the chatbot interface
@app.route("/")
def index():
    return render_template("index.html")

# API route: handles user input, generates text, image, and audio
@app.route("/api", methods=["POST"])
def api():
    # Get user's input from JSON payload
    user_input = request.json.get("message", "")

    # Format prompt for GPT: ask for a meal idea using these ingredients
    prompt = f"Please describe a meal I could make using only the following ingredients: {user_input}"

    try:
        # ------------------------------------------
        # Step 1: Get recipe text from GPT
        # ------------------------------------------
        recipe_response = openai_client.chat.completions.create(
            model="gpt-4.1",
            messages=[{"role": "user", "content": prompt}]
        )
        recipe = recipe_response.choices[0].message.content

        # ------------------------------------------
        # Step 2: Ask GPT to generate image prompt
        # ------------------------------------------
        image_prompt_response = openai_client.chat.completions.create(
            model="gpt-4.1",
            messages=[{
                "role": "user",
                "content": f"Give me a short description to use with DALL-E of the finished product of this recipe: {recipe}"
            }]
        )
        image_prompt = image_prompt_response.choices[0].message.content

        # ------------------------------------------
        # Step 3: Generate image with DALL·E 3
        # ------------------------------------------
        image = openai_client.images.generate(
            model="dall-e-3",
            prompt=image_prompt,
            size="1024x1024",
            quality="standard",
            n=1,
        )
        image_url = image.data[0].url  # Get the image URL

        # ------------------------------------------
        # Step 4: Ask GPT to generate a spoken script
        # ------------------------------------------
        voice_script_response = openai_client.chat.completions.create(
            model="gpt-4.1",
            messages=[{
                "role": "user",
                "content": f"Give me a short script of how to use the following recipe: {recipe}"
            }]
        )
        voice_script = voice_script_response.choices[0].message.content

        # ------------------------------------------
        # Step 5: Generate voice audio with ElevenLabs
        # ------------------------------------------
        audio = voice_client.text_to_speech.convert(
            voice_id=VOICE_ID,
            output_format="mp3_44100_128",
            text=voice_script,
            model_id="eleven_multilingual_v2",
        )
        audio_base64 = base64.b64encode(b"".join(audio)).decode("utf-8")  # Encode to base64 for browser

        # ------------------------------------------
        # Final Response: return all generated data
        # ------------------------------------------
        return jsonify({
            "text": recipe,
            "image_url": image_url,
            "audio_base64": audio_base64
        })

    except Exception as e:
        # If anything goes wrong, return an error
        return jsonify({"error": str(e)}), 500

# ------------------------------------------
# App runner
# ------------------------------------------
if __name__ == "__main__":
    app.run(debug=True)
