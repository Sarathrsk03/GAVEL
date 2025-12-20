from sentence_transformers import SentenceTransformer, util

# Load model (downloads once, cached locally)
model = SentenceTransformer("all-MiniLM-L6-v2")

text1 = "This is a contract"
text2 = "This agreement is valid"

# Generate embeddings (happens internally)
emb1 = model.encode(text1, convert_to_tensor=True)
emb2 = model.encode(text2, convert_to_tensor=True)

# Cosine similarity
score = util.cos_sim(emb1, emb2)

print(float(score))