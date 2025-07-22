# === File: app/utils/file_writer.py ===
# Utility to write structured content to a .txt file

import os
from datetime import datetime
import logging

# Output directory for generated files
OUTPUT_DIR = "static/outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def write_output_file(agent_name, output, filename, payload=None, prompt=None, context=None):
    """
    Write the output to a .txt file in static/outputs.
    If filename is provided, use it; otherwise, generate a default one.
    Returns (filename, full_output).

    Args:
        agent_name (str): Name of the agent.
        output (str): Final generated output.
        filename (str, optional): Custom filename for the output file.
        payload (dict, optional): Original request payload.
        prompt (str, optional): Prompt sent to GPT.
        context (str, optional): Additional user-supplied context.

    Returns:
        tuple: (filename, full_output)
    """
    # Always generate a timestamp for the footer
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # If no filename is provided, generate a default one
    if filename is None:
        filename = f"{agent_name.replace(' ', '_')}_{timestamp}.txt"

    # Ensure the outputs directory exists
    file_path = os.path.join(OUTPUT_DIR, filename)
    logging.warning(f"Writing file to: {file_path}")
    logging.warning(f"Absolute file path (write): {os.path.abspath(file_path)}")  # <-- Add this

    # Build the full output content (customize as needed)
    full_output = f"""
========================
🔵 AGENT: {agent_name}
========================

📤 REQUEST PAYLOAD
------------------------
{payload}

📋 FULL PROMPT SENT TO GPT
------------------------
{prompt}

📌 CONTEXT PROVIDED (User-Supplied Content)
------------------------
{context}

📈 GPT-Generated Output
------------------------
{output}

========================
📁 File generated on: {timestamp}
========================
"""

    # Write to file
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(full_output)
    logging.warning(f"File written successfully: {file_path}")

    return filename, full_output
