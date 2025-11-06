# test_similarity.py
"""
Test if llama3 embeddings can find ABC Corp
"""

import ollama
import json

print("="*70)
print("TESTING EMBEDDING SIMILARITY")
print("="*70)

# Load vendors
with open('data/vendors_clean.json', 'r') as f:
    data = json.load(f)

print(f"\n📋 Loaded {len(data['vendors'])} vendors")

# Generate query embedding
query = "ABC Corp payment"
print(f"\n🔍 Query: '{query}'")
print("Generating query embedding...")

query_response = ollama.embeddings(model='llama3', prompt=query)
query_embedding = query_response['embedding']

print(f"✅ Query embedding: {len(query_embedding)} dimensions")

# Calculate similarity for each vendor
print("\n" + "="*70)
print("CALCULATING SIMILARITY FOR EACH VENDOR:")
print("="*70)

import math

def cosine_similarity(vec1, vec2):
    """Calculate cosine similarity between two vectors"""
    dot_product = sum(a * b for a, b in zip(vec1, vec2))
    magnitude1 = math.sqrt(sum(a * a for a in vec1))
    magnitude2 = math.sqrt(sum(b * b for b in vec2))
    
    if magnitude1 == 0 or magnitude2 == 0:
        return 0
    
    return dot_product / (magnitude1 * magnitude2)


results = []

for vendor in data['vendors']:
    # Create vendor text (same as in rag_system.py)
    vendor_text = f"""
    Vendor: {vendor['name']}
    Account: {vendor['account_number']}
    Routing: {vendor['routing_number']}
    Bank: {vendor['bank_name']}
    Email: {vendor['contact_email']}
    Payment Terms: {vendor['payment_terms']}
    Notes: {vendor['notes']}
    """
    
    print(f"\nVendor: {vendor['name']}")
    print("  Generating embedding...")
    
    # Generate embedding
    vendor_response = ollama.embeddings(model='llama3', prompt=vendor_text.strip())
    vendor_embedding = vendor_response['embedding']
    
    # Calculate similarity
    similarity = cosine_similarity(query_embedding, vendor_embedding)
    
    print(f"  ✅ Similarity: {similarity:.4f}")
    
    results.append({
        'name': vendor['name'],
        'account': vendor['account_number'],
        'similarity': similarity
    })

# Sort by similarity
results.sort(key=lambda x: x['similarity'], reverse=True)

print("\n" + "="*70)
print("RANKED RESULTS:")
print("="*70)

for i, result in enumerate(results, 1):
    print(f"{i}. {result['name']}")
    print(f"   Account: {result['account']}")
    print(f"   Similarity: {result['similarity']:.4f}")
    print()

# Check if ABC Corp is top result
top_vendor = results[0]['name']
if 'ABC' in top_vendor or 'abc' in top_vendor.lower():
    print("✅ ABC Corp is the top result!")
else:
    print(f"❌ PROBLEM: Top result is '{top_vendor}', not ABC Corp")
    print("\n🔍 INVESTIGATION:")
    
    # Find ABC Corp in results
    abc_results = [r for r in results if 'ABC' in r['name'] or 'abc' in r['name'].lower()]
    
    if abc_results:
        abc_rank = results.index(abc_results[0]) + 1
        print(f"   ABC Corp is ranked #{abc_rank}")
        print(f"   ABC Corp similarity: {abc_results[0]['similarity']:.4f}")
        print(f"   Top vendor similarity: {results[0]['similarity']:.4f}")
        print(f"   Difference: {results[0]['similarity'] - abc_results[0]['similarity']:.4f}")
    else:
        print("   ❌ ABC Corp not found in any vendor names!")