import openai

def generate_marketing_post(topic, style="Engaging", length="Short"):
    prompt = f"""You are a creative marketing assistant for WB WHITE INSURANCE.
Generate a {length.lower()} social media post about: "{topic}".
Make it engaging, professional, and include a call to action.
Always mention WB WHITE INSURANCE as the company.
Style: {style}
"""
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content.strip()