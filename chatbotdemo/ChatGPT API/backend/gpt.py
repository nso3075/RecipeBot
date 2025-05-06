from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_meal_idea(ingredients, context):
    prompt = (
        f"Create a detailed dorm-friendly meal using ONLY these ingredients: {ingredients}.\n"
        f"Here is some context on those ingredients:\n{context}\n"
        "Format response with <h2>, <ul>, <li>, <p> HTML tags."
    )
    response = client.chat.completions.create(
        model="gpt-4.1",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

def generate_chat_response(user_input, ingredient_list):
    base = f"The user has these ingredients: {', '.join(ingredient_list)}.\n"
    prompt = base + "Answer their question: " + user_input + "\nFormat response with <h2>, <ul>, <li>, <p> HTML tags."
    response = client.chat.completions.create(
        model="gpt-4.1",
        messages=[{"role": "user", "content": prompt}]
    )
    return f"<p>{response.choices[0].message.content.strip()}</p>"

def generate_image_prompt(recipe_text):
    prompt = f"Describe a DALL-E 3 image prompt of the following meal:\n{recipe_text}"
    response = client.chat.completions.create(
        model="gpt-4.1",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

def generate_script(recipe_text):
    return f"Here's your recipe: {recipe_text}"
