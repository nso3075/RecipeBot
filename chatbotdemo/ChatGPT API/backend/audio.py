from elevenlabs.client import ElevenLabs
import os
import base64

from dotenv import load_dotenv

load_dotenv()

voice_client = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))
VOICE_ID = os.getenv("VOICE_ID")

def generate_audio(script: str) -> str:
    audio = voice_client.text_to_speech(
        voice_id = VOICE_ID,
        output_format = "mp3",
        text = script,
        model_id = "eleven_multilingual_v2",
    )
    
    # Convert audio to base64
    audio_base64 = base64.b64encode(b"".join(audio)).decode('utf-8')
    
    return audio_base64