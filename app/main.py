# === File: app/main.py ===
# Main Flask application setup

import logging
from flask import Flask, render_template, request, redirect, url_for, session
from app.routes.agent_router import agent_bp
from app.routes.health import health_bp
from app.services.seo_generator import run_seo_agent
from app.services.embedding_store import search_embeddings
from app.services.marketing_agent import generate_marketing_post
from app.services.google_docs import create_google_doc
import openai
import os
from google.auth.transport.requests import Request  # <-- Add this line
#from app.auth import login_manager, oauth  # or whatever you define in auth.py

app = Flask(__name__, template_folder="../templates")
app.secret_key = os.environ.get("SECRET_KEY", "dev")

# Registering the agent and health check routes
app.register_blueprint(agent_bp)
app.register_blueprint(health_bp)

# Welcome page route
@app.route("/")
def welcome():
    return render_template("welcome.html")


# Simple login route
@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if username == "admin" and password == "password":
            session["logged_in"] = True
            return redirect(url_for("welcome"))
        error = "Invalid credentials"
    return render_template("login.html", error=error)

# Content Generator Route (Classic and Agentic)
@app.route("/content-generator", methods=["GET", "POST"])
def content_generator():
    output = None
    download_url = None
    filename = None

    if request.method == "POST":
        # Get form data from the HTML form
        topic = request.form.get("topic")
        style = request.form.get("style")
        length = request.form.get("length")
        faqs = request.form.get("faqs")
        limit = request.form.get("limit")
        context = request.form.get("context")
        use_agentic = request.form.get("use_agentic") == "on"  # Checkbox in form

        # Build the payload for the agent
        payload = {
            "agent": "seo_generator",
            "input": {
                "topic": topic,
                "style": style,
                "length": length,
                "FAQ'S": faqs,
                "LIMIT": limit,
                "EXISTING DATA TO BE USED ": context
            }
        }
        try:
            if use_agentic:
                # Use agentic content generator (multi-step, LLM-reflective)
                output = agentic_content_generator(payload)
                filename = None
                download_url = None
            else:
                # Classic flow: run SEO agent and read generated file
                result = run_seo_agent(payload)
                if "filename" in result:
                    filename = result["filename"]
                    with open(filename, "r", encoding="utf-8") as f:
                        output = f.read()
                        # Replace placeholder with company name
                        output = output.replace("[Company Name]", "WB White Insurance")
                download_url = result.get("download_url")
        except Exception as e:
            # If there is an exception during the agent call, display it
            output = f"Exception: {e}"

    # Logging for debugging
    import logging
    logging.warning(f"Passing download_url to template: {download_url}")
    logging.warning(f"Passing filename to template: {filename}")

    # Render the template and pass the output (the extracted article or error) to be displayed
    return render_template(
        "index.html",
        output=output,
        download_url=download_url,
        filename=filename
    )

# RAG UI Route (Classic and Agentic)
@app.route("/rag-ui", methods=["GET", "POST"])
def rag_ui():
    import logging
    rag_answer = None
    retrieved_files = []
    use_agentic = False
    if request.method == "POST":
        use_agentic = request.form.get("use_agentic") == "on"  # Checkbox in form
        query = request.form.get("rag_query")
        if use_agentic:
            # Use agentic RAG (multi-step, LLM-reflective)
            rag_answer = agentic_rag(query)
            retrieved_files = []
        else:
            # Classic RAG: expand query, retrieve, build context, answer
            queries = expand_query_with_llm(query)
            all_results = []
            for q in queries:
                results = search_embeddings(q, top_k=2)
                # If results is a dict with "error", skip or handle
                if isinstance(results, dict) and "error" in results:
                    logging.error(f"RAG search error: {results['error']}")
                    continue
                all_results.extend(results)
            # Remove duplicate files
            seen = set()
            unique_results = []
            for r in all_results:
                if isinstance(r, dict) and "file" in r:
                    if r["file"] not in seen:
                        unique_results.append(r)
                        seen.add(r["file"])
            # Build context from retrieved files
            context = ""
            for res in unique_results:
                try:
                    with open(res["file"], "r", encoding="utf-8") as f:
                        context += f"\n---\n" + f.read()
                except Exception as e:
                    logging.error(f"Error reading file {res['file']}: {e}")
            # Prompt LLM with context and question
            prompt = f"""Use the following context to answer the user's question.

Context:
{context}

Question: {query}
Answer:"""
            try:
                response = openai.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt}]
                )
                rag_answer = response.choices[0].message.content
            except Exception as e:
                logging.error(f"OpenAI API error: {e}")
                rag_answer = f"Exception: {e}"
            retrieved_files = [r["file"] for r in unique_results]
    # Render the RAG UI template with the answer and files used
    return render_template("rag.html", rag_answer=rag_answer, retrieved_files=retrieved_files)

# Marketing Post Generator Route
@app.route("/marketing-post", methods=["GET", "POST"])
def marketing_post():
    post = None         # The generated marketing post text
    doc_url = None      # The URL of the created Google Doc
    error = None        # Any error message to display to the user

    if request.method == "POST":
        # Get form data from the HTML form
        topic = request.form.get("topic")
        style = request.form.get("style", "Engaging")
        length = request.form.get("length", "Short")
        # Generate the marketing post using the LLM agent
        post = generate_marketing_post(topic, style, length)
        try:
            # Try to create a Google Doc with the generated post
            doc_url = create_google_doc(f"WB WHITE INSURANCE - {topic}", post)
        except Exception as e:
            # If there is an error creating the Google Doc, capture the error message
            error = f"Google Docs error: {e}"
    # Render the template, passing the generated post, Google Doc URL, and any error
    return render_template("marketing_post.html", post=post, doc_url=doc_url, error=error)

# LLM-powered Query Expansion for RAG
def expand_query_with_llm(query):
    prompt = f"Suggest 3 alternative phrasings or synonyms for this insurance-related question: '{query}'"
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    suggestions = response.choices[0].message.content.split('\n')
    queries = [query] + [s.strip('- ').strip() for s in suggestions if s.strip()]
    return queries

def call_llm(payload):
    """
    Calls OpenAI's chat completion API with the given payload.
    If payload is a dict with a 'content' key, use that as the prompt.
    If payload is a string, use it directly as the prompt.
    """
    if isinstance(payload, dict) and "content" in payload:
        prompt = payload["content"]
    else:
        prompt = str(payload)
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content.strip()


# Agentic Content Generator (LLM self-reflection)
def agentic_content_generator(payload):
    # Step 1: Generate initial content
    content = call_llm(payload)
    # Step 2: Ask LLM if more info is needed
    prompt = f"""Here is the generated content:
{content}
Is this content sufficient for the user's needs? If not, what should be added or clarified?"""
    reflection = call_llm({"content": prompt})
    if "add" in reflection.lower() or "clarify" in reflection.lower():
        # Optionally, ask user for more info or let LLM add details
        content += "\n\n" + call_llm({"content": "Add the missing details."})
    return content

# Agentic RAG (LLM self-assessment and suggestion)
def agentic_rag(query):
    queries = expand_query_with_llm(query)
    all_results = []
    for q in queries:
        results = search_embeddings(q, top_k=2)
        # If results is a dict with "error", skip or handle
        if isinstance(results, dict) and "error" in results:
            logging.error(f"RAG search error: {results['error']}")
            continue
        all_results.extend(results)
    # Remove duplicates
    seen = set()
    unique_results = []
    for r in all_results:
        if r["file"] not in seen:
            unique_results.append(r)
            seen.add(r["file"])
    # Build context from all unique results
    context = "\n---\n".join([open(r["file"], encoding="utf-8").read() for r in unique_results])
    # Step 1: Ask LLM for answer and self-assessment
    prompt = f"""Use the following context to answer the user's question.

Context:
{context}

Question: {query}
Answer the question. If the context is not sufficient, suggest a new search query or ask the user for clarification."""
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    answer = response.choices[0].message.content
    # Step 2: If LLM suggests a new query or clarification, handle accordingly (loop or ask user)
    if "suggest" in answer.lower() or "clarify" in answer.lower():
        # Optionally, repeat retrieval or ask user for more info
        pass
    return answer

# Example return from run_seo_agent
# return {"filename": "static/outputs/SEO and GEO Generator_20250625_2232.txt"}
