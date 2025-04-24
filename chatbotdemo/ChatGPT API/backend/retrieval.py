import json
import faiss
import numpy as np
from openai import OpenAI
import os

openai_client = OpenAI(api_key=os.getenv("KEY")) # Replace later

# Load ingredients
with open("data/ingredients.json") as f:
    facts = json.load(f)

# Embed text string
def embed_text(text):
    response = openai_client.embeddings.create(
        model="text-embedding-ada-002",
        input=[text]
    )
    return np.array(response.data[0].embedding, dtype="float32")

# Build FAISS index from ingredients
text_data = [f"{item['name']}: {item['summary']} Pairs well with: {', '.join(item['pairs_well_with'])}" for item in facts]
embedding_dim = len(embed_text("sample"))
index = faiss.IndexFlatL2(embedding_dim)
index.add(np.array([embed_text(t) for t in text_data]))

# Retrieve top-k ingredient facts
def get_ingredient_context(user_input, top_k=5):
    query_vec = embed_text(user_input).reshape(1, -1)
    _, indices = index.search(query_vec, top_k)
    
    return "\n\n".join([
        f"{facts[i]['name']}: {facts[i]['summary']}\nPairs well with: {', '.join(facts[i]['pairs_well_with'])}\nTips: {facts[i]['cooking_tips']}"
        for i in indices[0]
    ])
