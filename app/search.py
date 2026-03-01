import json
import time
import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

print("Loading AI model (all-MiniLM-L6-v2)...")
model = SentenceTransformer('all-MiniLM-L6-v2')

def load_data(filepath):
    with open(filepath, 'r') as file:
        raw_data = json.load(file)
    df = pd.DataFrame(raw_data['claims'])
    
    # Combine description and key factors
    df['searchable_text'] = df['description'] + " Key factors: " + df['key_factors'].apply(lambda x: ", ".join(x))
    return df

print("Loading large dataset...")
# Pointing to our new 1,000 record dataset!
df = load_data('large_claims_data.json')

print(f"Embedding {len(df)} historical claims... (This will take a few seconds)")
historical_embeddings = model.encode(df['searchable_text'].tolist())
print("Ready!")

def find_similar_claims(new_claim_text):
    start_time = time.time() 
    
    query_embedding = model.encode([new_claim_text])
    similarities = cosine_similarity(query_embedding, historical_embeddings)[0]
    
    # Sort ALL indices from highest similarity to lowest
    top_indices = similarities.argsort()[::-1]
    
    results = df.iloc[top_indices].copy()
    results['Similarity_Score'] = similarities[top_indices]
    
    end_time = time.time() 
    search_time = end_time - start_time
    
    return results, search_time