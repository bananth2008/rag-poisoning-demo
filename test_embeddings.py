# Quick test script - save as test_embeddings.py
import ollama

print("Testing Ollama embeddings API...")

try:
    response = ollama.embeddings(
        model='llama3',
        prompt='test'
    )
    
    print(f"✅ API works!")
    print(f"Embedding length: {len(response['embedding'])}")
    print(f"First 5 values: {response['embedding'][:5]}")
    print(f"Sample value range: min={min(response['embedding']):.3f}, max={max(response['embedding']):.3f}")
    
except Exception as e:
    print(f"❌ Error: {e}")