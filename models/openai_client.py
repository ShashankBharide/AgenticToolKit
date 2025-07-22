# === File: models/openai_client.py ===
# Wrapper around OpenAI API call
from http.client import HTTPException
import openai
import os
from dotenv import load_dotenv


load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def generate_content(prompt):
    try:
        client = openai.OpenAI(api_key=openai.api_key)
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful SEO and GEO content assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=2000,  # Increase this as needed
            temperature=0.7,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error: {e}")
        return None

