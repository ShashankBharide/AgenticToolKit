import openai
import os
import faiss
import numpy as np
import pickle
import logging

# --- PRODUCTION-FRIENDLY PATHS ---
# Get the absolute path to the current file's directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Define the absolute path to the outputs directory (for storing files and FAISS index)
OUTPUT_DIR = "/home/ubuntu/AgenticToolKit/static/outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)  # Ensure the outputs directory exists

# Define the absolute paths for the FAISS index and metadata files
INDEX_PATH = os.path.join(OUTPUT_DIR, "faiss.index")
META_PATH = os.path.join(OUTPUT_DIR, "faiss_meta.pkl")


def get_latest_file_by_topic(topic, outputs_dir=OUTPUT_DIR):
    """
    Find the latest .txt file in outputs_dir whose filename contains the topic.
    Returns the absolute path to the latest file, or None if not found.
    """
    files = [
        f for f in os.listdir(outputs_dir)
        if topic.lower() in f.lower() and f.endswith(".txt")
    ]
    if not files:
        return None
    # Sort files by last modified time (descending)
    files.sort(key=lambda f: os.path.getmtime(os.path.join(outputs_dir, f)), reverse=True)
    return os.path.join(outputs_dir, files[0])

def store_embedding(file_path, topic=None):
    """
    Loads the latest file for the given topic, generates an embedding using OpenAI,
    and stores it in a FAISS index along with metadata.
    Returns info about the stored embedding or an error message.
    """
    if not os.path.exists(file_path):
        return {"error": f"No file found for topic '{file_path}'."}
    try:
        # Read the file content
        try:
            # Make sure file path uses forward slashes
            file_path = file_path.replace("\\", "/")
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            logging.error(f"Error reading file {file_path}: {e}")
            return {"error": f"Could not read file: {e}"}
        
        # Generate embedding using OpenAI API
        try:
            response = openai.embeddings.create(
                input=content,
                model="text-embedding-3-small"
            )
            embedding = np.array(response.data[0].embedding, dtype="float32").reshape(1, -1)
        except Exception as e:
            logging.error(f"OpenAI embedding error: {e}")
            return {"error": f"OpenAI embedding error: {e}"}

        # Log the embedding creation for debugging
        logging.warning(f"Embedding created for topic: {topic}, file: {file_path}, embedding_dim: {len(embedding)}")

        # Load existing FAISS index and metadata, or create new ones if they don't exist
        try:
            if os.path.exists(INDEX_PATH):
                index = faiss.read_index(INDEX_PATH)
                with open(META_PATH, "rb") as meta_f:
                    meta = pickle.load(meta_f)
            else:
                index = faiss.IndexFlatL2(embedding.shape[1])
                meta = []
        except Exception as e:
            logging.error(f"Error loading FAISS index or metadata: {e}")
            return {"error": f"Error loading FAISS index or metadata: {e}"}

        # Add the new embedding and its metadata
        index.add(embedding)
        meta.append({"topic": topic, "file": file_path})

        # Save the updated FAISS index and metadata to disk
        try:
            faiss.write_index(index, INDEX_PATH)
            with open(META_PATH, "wb") as meta_f:
                pickle.dump(meta, meta_f)
        except Exception as e:
            logging.error(f"Error saving FAISS index or metadata: {e}")
            return {"error": f"Error saving FAISS index or metadata: {e}"}

        return {
            "file": file_path,
            "embedding_dim": embedding.shape[1],
            "index_size": index.ntotal
        }
    except Exception as e:
        logging.error(f"Unexpected error in store_embedding: {e}")
        return {"error": f"Unexpected error: {e}"}

def search_embeddings(query, top_k=3):
    """
    Given a query string, generate its embedding and retrieve the top_k most similar documents
    from the FAISS index. Returns a list of dicts with file, topic, and similarity score.
    """
    try:
        # Check if the FAISS index and metadata exist
        if not os.path.exists(INDEX_PATH) or not os.path.exists(META_PATH):
            return {"error": "No embeddings index found."}

        # Generate embedding for the query using OpenAI API
        try:
            response = openai.embeddings.create(
                input=query,
                model="text-embedding-3-small"
            )
            query_embedding = np.array(response.data[0].embedding, dtype="float32").reshape(1, -1)
        except Exception as e:
            logging.error(f"OpenAI embedding error: {e}")
            return {"error": f"OpenAI embedding error: {e}"}

        # Load FAISS index and metadata from disk
        try:
            index = faiss.read_index(INDEX_PATH)
            with open(META_PATH, "rb") as meta_f:
                meta = pickle.load(meta_f)
        except Exception as e:
            logging.error(f"Error loading FAISS index or metadata: {e}")
            return {"error": f"Error loading FAISS index or metadata: {e}"}

        # Search for top_k similar embeddings in the index
        try:
            D, I = index.search(query_embedding, top_k)
            results = []
            for idx, score in zip(I[0], D[0]):
                if idx < len(meta):
                    results.append({
                        "file": meta[idx]["file"].replace("\\", "/"),
                        "topic": meta[idx]["topic"],
                        "score": float(score)
                    })
            return results
        except Exception as e:
            logging.error(f"Error during FAISS search: {e}")
            return {"error": f"Error during FAISS search: {e}"}
    except Exception as e:
        logging.error(f"Unexpected error in search_embeddings: {e}")
        return {"error": f"Unexpected error: {e}"}