import os
import faiss
import numpy as np
import pdfplumber
from sentence_transformers import SentenceTransformer
import warnings
import json

# Suppress warnings for cleaner output
warnings.filterwarnings("ignore")

# ✅ Allowed year folders
ALLOWED_YEARS = {"1995", "1996", "2000", "2002"}

def extract_text_from_pdf(pdf_path):
    try:
        text = ""
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        return text
    except Exception as e:
        print(f"Error reading {pdf_path}: {e}")
        return ""

def chunk_text(text, chunk_size=500, overlap=50):
    chunks = []
    if not text:
        return chunks
    
    for i in range(0, len(text), chunk_size - overlap):
        chunks.append(text[i:i + chunk_size])
    return chunks

def create_embeddings(dataset_path, index_path, metadata_path):
    print(f"Loading model...")
    model = SentenceTransformer('all-MiniLM-L6-v2')
    embedding_dim = 384
    
    index = faiss.IndexFlatL2(embedding_dim)
    metadata = {}
    doc_id = 0
    
    print(f"Scanning dataset at {dataset_path}...")
    
    files_files = []
    for root, dirs, files in os.walk(dataset_path):
        rel_path = os.path.relpath(root, dataset_path)
        path_parts = rel_path.split(os.sep)

        # ✅ Year is second-level folder
        if len(path_parts) < 2:
            continue

        year_folder = path_parts[1]
        if year_folder not in ALLOWED_YEARS:
            continue

        for file in files:
            if file.lower().endswith('.pdf'):
                files_files.append(os.path.join(root, file))
    
    print(f"Found {len(files_files)} PDF files.")
    
    batch_sentences = []
    batch_metadata = []
    batch_size = 64
    
    for filepath in files_files:
        print(f"Processing: {filepath}")
        text = extract_text_from_pdf(filepath)
        chunks = chunk_text(text)
        
        for chunk in chunks:
            batch_sentences.append(chunk)
            batch_metadata.append({
                "id": doc_id,
                "source": filepath,
                "text": chunk
            })
            doc_id += 1
            
            if len(batch_sentences) >= batch_size:
                embeddings = model.encode(batch_sentences)
                index.add(np.array(embeddings).astype('float32'))
                
                for meta in batch_metadata:
                    metadata[meta["id"]] = meta
                
                batch_sentences = []
                batch_metadata = []

    if batch_sentences:
        embeddings = model.encode(batch_sentences)
        index.add(np.array(embeddings).astype('float32'))
        for meta in batch_metadata:
            metadata[meta["id"]] = meta

    faiss.write_index(index, index_path)
    
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=4)
        
    print("Done!")

base_dir = os.path.dirname(os.path.abspath(__file__))
dataset_dir = os.path.join(base_dir, "kanoon-dataset")
index_file = os.path.join(base_dir, "kanoon_faiss_index.bin")
metadata_file = os.path.join(base_dir, "kanoon_metadata.json")
    
if os.path.exists(dataset_dir):
    create_embeddings(dataset_dir, index_file, metadata_file)
else:
    print(f"Dataset directory not found at {dataset_dir}")
