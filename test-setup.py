# test_setup.py
"""
Test script to verify all installations
"""

print("Testing imports...")

try:
    import streamlit as st
    print("✅ Streamlit installed")
except ImportError as e:
    print(f"❌ Streamlit error: {e}")

try:
    import pandas as pd
    print("✅ Pandas installed")
except ImportError as e:
    print(f"❌ Pandas error: {e}")

try:
    import numpy as np
    print("✅ NumPy installed")
except ImportError as e:
    print(f"❌ NumPy error: {e}")

try:
    import ollama
    print("✅ Ollama installed")
except ImportError as e:
    print(f"❌ Ollama error: {e}")

try:
    import chromadb
    print("✅ ChromaDB installed")
except ImportError as e:
    print(f"❌ ChromaDB error: {e}")

try:
    from sentence_transformers import SentenceTransformer
    print("✅ Sentence Transformers installed")
except ImportError as e:
    print(f"❌ Sentence Transformers error: {e}")

print("\n" + "="*50)
print("Testing Ollama connection...")
print("="*50)

try:
    response = ollama.chat(
        model='llama3',
        messages=[{'role': 'user', 'content': 'Say "Hello" if you can hear me'}]
    )
    print(f"✅ Ollama connected: {response['message']['content']}")
except Exception as e:
    print(f"❌ Ollama error: {e}")
    print("   Make sure Ollama is running: ollama serve")

print("\n" + "="*50)
print("✅ SETUP COMPLETE!" if all else "⚠️ Fix errors above")
print("="*50)