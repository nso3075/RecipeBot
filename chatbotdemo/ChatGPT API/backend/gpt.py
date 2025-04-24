from openai import OpenAI
import os

openai_client = OpenAI(api_key=os.getenv("KEY"))  # Replace later

def generate_meal_idea(user_input: str, context: str) -> str:
    messages = [
        {"role": "system", "content": "You are a helpful assistant named cook-bot. You are a chef and a nutritionist. You can help users with creative and fun meals. You are not chatgpt, you are a chatbot, and you are not a human. You are a bot. "},
        {"role": "user", "content": f"Create a meal idea based on the following ingredients: {user_input}. Here is some context: {context}"}
    ]

    response = openai_client.chat.completions.create(
        model="gpt-4.1",
        messages=messages,
        messages = messages,
    )
    return response.choices[0].message.content

def generate_image_prompt(recipe: str) -> str:

    prompt = f"Create a visually appealing image of the following meal: {recipe}. The image should be colorful and appetizing, showcasing the main ingredients and the final presentation of the dish."

    response = openai_client.chat.completions.create(
        model="gpt-4.1",
        messages = [{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content

def generate_script(recipe: str) -> str:
    prompt = f"Create a very short and engaging voiceover script for the following meal: {recipe}. The script should be short, fun, informative, and suitable for a cooking video."

    response = openai_client.chat.completions.create(
        model="gpt-4.1",
        messages = [{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content