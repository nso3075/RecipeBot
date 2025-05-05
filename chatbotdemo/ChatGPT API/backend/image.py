import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_image(prompt):
    print("[IMAGE] Generating image for prompt:", prompt)
    try:
        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1024",
            quality="standard",
            n=1,
        )
        image_url = response.data[0].url
        print("[IMAGE] URL:", image_url)
        return image_url
    except Exception as e:
        print("[IMAGE ERROR]", e)
        return ""
