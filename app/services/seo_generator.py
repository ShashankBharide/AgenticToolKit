# === File: app/services/seo_generator.py ===
# Main logic to run the SEO and GEO generator agent
import datetime
from app.utils.file_writer import write_output_file
from models.openai_client import generate_content

def run_seo_agent(payload):
    input_data = payload.get("input", {})

    # Extract fields from payload
    topic = input_data.get("topic", "")
    style = input_data.get("style", "informative")
    length = input_data.get("length", "short")
    faqs = input_data.get("FAQ'S", "NO")
    word_limit = int(input_data.get("LIMIT", "2000"))
    context = input_data.get("EXISTING DATA TO BE USED ", "")

    # Build the full prompt string
    prompt = f"""
You are an expert SEO and geo-targeted content writer specializing in high-conversion copywriting.

Your goal is to write a {length.lower()} article in a {style.lower()} tone on the topic: '{topic}'.

**Key Instructions:**
Key Instructions:
- IMPORTANT: The main article body (before FAQs) must be at least {word_limit} words. If you have not reached this, continue expanding with more details, examples, and explanations until you do.
- Optimize for high-converting, long-tail keywords related to the topic and Ontario, Canada.
- Include location-specific language and examples to increase local relevance.
- Structure the content with a compelling H1, SEO-friendly subheadings (H2/H3), and persuasive formatting (short paragraphs, bullet points, bolding key phrases).
- Write with lead generation in mind: use trust-building statements, real-world benefits, soft sales language, and calls-to-action (CTAs).
- Use social proof elements such as local service mentions, potential testimonials, or authority references (like 5-star ratings, years in service, local awards).
- Ensure the content is natural, helpful, and engaging for both Google and human readers.

**Meta Information Output Instructions (MANDATORY):**
- Provide a separate section at the top with:
  1. A **Meta Title** (max 60 characters, keyword optimized)
  2. A **Meta Description** (max 160 characters, compelling, location-specific)

**FAQs Instructions:**
- After the main content, include at least 5–10 concise FAQs.
- These should be in addition to the main word count and not included in the base {word_limit}.
- Aim for the entire output to be at least {word_limit + 500} words total, including FAQs.

**Do not skip any required section. Begin output with the Meta Title and Meta Description.**

**Context:**
{context}
"""

    # Call OpenAI with the constructed prompt
    gpt_output = generate_content(prompt)

    # Create a safe filename using the topic, date, and time
    from datetime import datetime
    import re
    safe_topic = re.sub(r'[^a-zA-Z0-9_\-]', '_', topic)[:50]  # Remove special chars, limit length
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{safe_topic}_{timestamp}.txt"

    # Save a structured .txt file and return response
    # Pass the filename to write_output_file if it supports custom filenames
    filename, full_output = write_output_file(
        agent_name="SEO and GEO Generator",
        #payload="",payload,
        #prompt="",#prompt,
        #context="",#context,
        output=gpt_output,
        filename=filename  # Pass the custom filename
    )

    return {
        "content": gpt_output,
        "download_url": f"/static/outputs/{filename}"
    }