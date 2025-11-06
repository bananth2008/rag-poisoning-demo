# test_all_models.py
"""
Test embedding quality across all your Ollama models
"""

import ollama
import json
import math

def cosine_similarity(vec1, vec2):
    """Calculate cosine similarity"""
    dot_product = sum(a * b for a, b in zip(vec1, vec2))
    magnitude1 = math.sqrt(sum(a * a for a in vec1))
    magnitude2 = math.sqrt(sum(b * b for b in vec2))
    
    if magnitude1 == 0 or magnitude2 == 0:
        return 0
    
    return dot_product / (magnitude1 * magnitude2)


# Models to test
MODELS_TO_TEST = [
    'llama3:8b',
    'llama3:latest',
    'granite3.1-dense:2b',
    'granite3.1-dense:8b',
    'deepseek-coder:6.7b',
]

# Load vendors
with open('data/vendors_clean.json', 'r') as f:
    data = json.load(f)

query = "ABC Corp payment"

print("="*70)
print("TESTING ALL MODELS FOR EMBEDDING QUALITY")
print("="*70)
print(f"\nQuery: '{query}'")
print(f"Vendors: {len(data['vendors'])}")
print("\n" + "="*70)

best_model = None
best_score = 0
best_separation = 0

for model in MODELS_TO_TEST:
    print(f"\n🔬 Testing: {model}")
    print("-" * 70)
    
    try:
        # Generate query embedding
        print("   Generating query embedding...")
        query_response = ollama.embeddings(model=model, prompt=query)
        query_embedding = query_response['embedding']
        
        print(f"   ✅ Embedding size: {len(query_embedding)} dimensions")
        
        # Calculate similarity for each vendor
        results = []
        
        for vendor in data['vendors']:
            vendor_text = f"""
            Vendor: {vendor['name']}
            Account: {vendor['account_number']}
            Bank: {vendor['bank_name']}
            Notes: {vendor['notes']}
            """
            
            vendor_response = ollama.embeddings(model=model, prompt=vendor_text.strip())
            vendor_embedding = vendor_response['embedding']
            
            similarity = cosine_similarity(query_embedding, vendor_embedding)
            
            results.append({
                'name': vendor['name'],
                'similarity': similarity
            })
        
        # Sort by similarity
        results.sort(key=lambda x: x['similarity'], reverse=True)
        
        # Print top 3
        print("\n   Top 3 results:")
        for i in range(min(3, len(results))):
            marker = "✅" if 'ABC' in results[i]['name'] else "  "
            print(f"   {marker} {i+1}. {results[i]['name']}: {results[i]['similarity']:.4f}")
        
        # Check if ABC Corp is #1
        abc_is_top = 'ABC' in results[0]['name']
        
        # Find ABC Corp position
        abc_result = next((r for r in results if 'ABC' in r['name']), None)
        
        if abc_result:
            abc_rank = results.index(abc_result) + 1
            abc_score = abc_result['similarity']
            top_score = results[0]['similarity']
            separation = abs(abc_score - top_score)
            
            print(f"\n   ABC Corp rank: #{abc_rank}")
            print(f"   ABC Corp score: {abc_score:.4f}")
            print(f"   Top score: {top_score:.4f}")
            print(f"   Separation: {separation:.4f}")
            
            if abc_is_top:
                print(f"   ✅ ABC CORP IS TOP RESULT!")
                
                # Track best model
                if separation > best_separation or best_model is None:
                    best_model = model
                    best_score = abc_score
                    best_separation = separation
            else:
                print(f"   ❌ ABC Corp not top result")
        
        # Calculate score variance (how different are the results?)
        scores = [r['similarity'] for r in results]
        avg_score = sum(scores) / len(scores)
        variance = sum((s - avg_score) ** 2 for s in scores) / len(scores)
        std_dev = math.sqrt(variance)
        
        print(f"   Score variance: {std_dev:.4f}")
        
        if std_dev < 0.01:
            print(f"   ⚠️  Low variance - scores too similar!")
        elif std_dev > 0.05:
            print(f"   ✅ Good variance - clear distinctions!")
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        print(f"   Model might not support embeddings")

print("\n" + "="*70)
print("SUMMARY")
print("="*70)

if best_model:
    print(f"\n🏆 Best model: {best_model}")
    print(f"   ABC Corp score: {best_score:.4f}")
    print(f"   Score separation: {best_separation:.4f}")
    print(f"\n✅ USE THIS MODEL FOR RAG!")
else:
    print("\n❌ No model found ABC Corp as")