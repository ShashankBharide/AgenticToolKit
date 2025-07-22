import sys
import os
import pickle

# Ensure project root is in sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from app.services.embedding_store import store_embedding

outputs_dir = "static/outputs"
index_path = os.path.join(outputs_dir, "faiss.index")
meta_path = os.path.join(outputs_dir, "faiss_meta.pkl")

# Load existing embedded files if meta exists
embedded_files = set()
if os.path.exists(meta_path):
    with open(meta_path, "rb") as f:
        meta = pickle.load(f)
        embedded_files = {entry["file"] for entry in meta}

# Step 1: Remove existing embeddings index and meta files (optional, comment out if you want to keep old embeddings)
# if os.path.exists(index_path):
#     os.remove(index_path)
#     print("Deleted existing faiss.index")
# if os.path.exists(meta_path):
#     os.remove(meta_path)
#     print("Deleted existing faiss_meta.pkl")

# Step 2: Embed only new .txt files not already embedded
for filename in os.listdir(outputs_dir):
    if filename.endswith(".txt"):
        file_path = os.path.join(outputs_dir, filename)
        if file_path in embedded_files:
            print(f"Already embedded: {file_path}")
            continue
        # Extract topic from filename (remove extension and timestamp if present)
        topic = filename.rsplit("_", 1)[0].replace("_", " ")
        print(f"Embedding for topic: {topic}")
        if not os.path.exists(file_path):
            print(f"File does not exist: {file_path}")
        else:
            print(f"File exists: {file_path}")
            try:
                result = store_embedding(file_path, topic)
                print(f"Success: {result}")
            except Exception as e:
                print(f"Failed for {filename}: {e}")