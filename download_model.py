# download_model.py
"""
Download sentence-transformers model
"""

from sentence_transformers import SentenceTransformer

print("Downloading sentence-transformers model...")
print("This may take 2-3 minutes...")

try:
    model = SentenceTransformer('all-MiniLM-L6-v2')
    print("✅ Model downloaded successfully!")
    print(f"Model location: {model._model_card_vars}")
    
    # Test it
    test_embedding = model.encode("test")
    print(f"✅ Model working! Embedding size: {len(test_embedding)}")
    
except Exception as e:
    print(f"❌ Error: {e}")
    print("\nTroubleshooting:")
    print("1. Check internet connection")
    print("2. Check if you're behind a proxy/firewall")
    print("3. Try Option 2 (use Ollama instead)")