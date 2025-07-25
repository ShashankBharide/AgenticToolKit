import openai

def generate_marketing_post(topic, style, length):
    prompt = f"""
    Create a {style.lower()} marketing post about {topic} for WB White Insurance.
    Length: {length}
    
    Requirements:
    - Professional tone
    - Focus on insurance benefits
    - Include relevant hashtags
    - DO NOT include any emojis or emoticons
    - Use only text and words
    - Keep it clean and professional
    
    Topic: {topic}
    """
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content.strip()