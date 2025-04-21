from flask import Flask, render_template, request, jsonify
from openai import OpenAI
from elevenlabs.client import ElevenLabs
import base64

# Initialize Flask
app = Flask(__name__)

# API Keys
OPENAI_API_KEY = "KEY"
ELEVENLABS_API_KEY = "KEY"
VOICE_ID = "KEY"

# Clients
openai_client = OpenAI(api_key=OPENAI_API_KEY)
voice_client = ElevenLabs(api_key=ELEVENLABS_API_KEY)

# Routes
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api", methods=["POST"])
def api():
    user_input = request.json.get("message", "")
    prompt = f"Please describe a meal I could make using only the following ingredients: {user_input}"

    try:
        # Step 1: Recipe from GPT
        recipe_response = openai_client.chat.completions.create(
            model="gpt-4.1",
            messages=[{"role": "user", "content": prompt}]
        )
        recipe = recipe_response.choices[0].message.content

        # Step 2: Image prompt
        image_prompt_response = openai_client.chat.completions.create(
            model="gpt-4.1",
            messages=[{
                "role": "user",
                "content": "Give me a short description to use with DALL-E of the finished product of this recipe: " + recipe
            }]
        )
        image_prompt = image_prompt_response.choices[0].message.content

        # Step 3: Generate image
        image = openai_client.images.generate(
            model="dall-e-3",
            prompt=image_prompt,
            size="1024x1024",
            quality="standard",
            n=1,
        )
        image_url = image.data[0].url

        # Step 4: Voice script generation
        voice_script_response = openai_client.chat.completions.create(
            model="gpt-4.1",
            messages=[{
                "role": "user",
                "content": "Give me a short script of how to use the following recipe: " + recipe
            }]
        )
        voice_script = voice_script_response.choices[0].message.content

        # Step 5: ElevenLabs speech
        audio = voice_client.text_to_speech.convert(
            voice_id=VOICE_ID,
            output_format="mp3_44100_128",
            text=voice_script,
            model_id="eleven_multilingual_v2",
        )
        audio_base64 = base64.b64encode(b"".join(audio)).decode("utf-8")

        return jsonify({
            "text": recipe,
            "image_url": image_url,
            "audio_base64": audio_base64
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
