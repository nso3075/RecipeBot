# RecipeBot
A voice enabled, image generating recipe assistant for college students, powered by the OpenAI API, ElevenLabs API, and Retrieval-Augmented Generation (RAG).

## Features
RAG-Backed GPT for intelligent recipe generation and ingredient substitution.
ElevenLabs API for voice synthesis.
DALL-E support to visualize the final dish.
Dual Modes:
- Recipe Mode for building recipes out of ingredients
- Chat Mode for food advice, recipie substitutions, and cooking tips.
Simple HTML frontend and a Flask based backend.

## Requirements
Python 3.10+
pip or venv
OpenAI API key
ElevenLabs API key and Voice ID

## Installation
1. Clone the Repo
```bash
git clone https://github.com/nso3075/RecipeBot.git
cd chatbotdemo/"ChatGPT API"
```
2. Create and Activate a Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
```
3. Install Dependencies
```bash
pip install -r requirements.txt
```

## Environment Setup
1. Create a `.env` file in the root directory.
2. Add your OpenAI and ElevenLabs API keys and Voice ID:
```env
OPENAI_API_KEY=your_openai_api_key
ELEVENLABS_API_KEY=your_elevenlabs_api_key
ELEVENLABS_VOICE_ID=your_elevenlabs_voice_id
```

## Running the Application
From the project root:
```bash
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
flask run
```

Then open your browser and go to:
http://127.0.0.1:5000

## Project Structure
```
app.py
.env
requirements.txt
templates/
    index.html
static/
    style.css
    ingredients.json
    images/
        gpt.jpg
        henry.jpg
        user.png
backend/
    gpt.py
    image.py
    audio.py
    retreival.py
README.md
```

## Modes
* 1: Recipe Mode---Build recipes from ingredients.
* 2: Chat Mode---Get food advice, recipe substitutions, and cooking tips.
* Reset---Reset the conversation.