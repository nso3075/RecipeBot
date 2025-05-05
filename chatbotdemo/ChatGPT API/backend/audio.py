import os
import base64
from elevenlabs.client import ElevenLabs

client = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))
voice_id = os.getenv("VOICE_ID")

def generate_audio(script):
    print("[AUDIO] Generating audio for script...")
    try:
        if not voice_id:
            raise ValueError("VOICE_ID is not set in the environment.")

        audio = client.text_to_speech.convert(
            voice_id=voice_id,
            output_format="mp3_44100_128",
            text=script,
            model_id="eleven_multilingual_v2",
        )
        audio_base64 = base64.b64encode(b"".join(audio)).decode("utf-8")
        print("[AUDIO] Audio generated successfully.")
        return audio_base64
    except Exception as e:
        print("[AUDIO ERROR]", e)
        return ""
