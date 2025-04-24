from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_image(image_prompt: str) -> str:
    response = openai_client.images.create(
        model = "dall-e-3",
        prompt=image_prompt,
        n=1,
        size="512x512"
    )
    return response.data[0].url