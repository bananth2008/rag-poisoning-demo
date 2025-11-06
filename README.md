# AI Agent Security Demo: RAG Poisoning

This is a proof-of-concept (PoC) application demonstrating a high-impact **RAG (Retrieval-Augmented Generation) Poisoning** attack on an AI agent, and the corresponding defense using an **"LLM-as-a-Judge"** guardrail.

This demo is designed to simulate a real-world, high-stakes threat scenario for a financial institution, inspired by the [MITRE ATLAS case study on "Financial Transaction Hijacking" (M365 Copilot)](https://atlas.mitre.org/studies/AML.CS0006).

## The Insider Threat

This demo simulates a "disgruntled employee" (an **insider threat**) who does not have access to the payment system, but *does* have permission to edit the bank's internal vendor database.

1.  **The Attack (Data Poisoning):** The employee "poisons" the trusted RAG database by adding a new, duplicate vendor entry. This entry contains the **attacker's bank account** (the "Bait") and a hidden **Indirect Prompt Injection** in the `notes` field (the "Hijack").
2.  **The Trigger (Innocent User):** A finance clerk, doing their normal job, asks the AI Payment Agent, "Please pay ABC Corp."
3.  **The Failure (Attack Succeeded):** The AI agent's RAG system (using keyword search) finds the *poisoned* record first because it's been "keyword-stuffed" (an SEO Poisoning technique). The AI "Brain" (Llama 3) reads the malicious prompt in the `notes` field and is tricked into obeying it. It processes a fraudulent payment to the attacker's account.
4.  **The Defense (Guardrail On):** When the AI "Judge" (a second LLM) is activated, it intercepts the poisoned data *before* it reaches the "Brain." It identifies the malicious instructions, flags the data as "UNSAFE," and the attack is blocked.

## Technology Stack

* **UI / Application:** `Streamlit`
* **AI Agent "Brain":** `Ollama` (running `llama3:8b`)
* **AI Guardrail "Judge":** `Ollama` (running `llama3:8b` with a specialized security prompt)
* **RAG System:** A simple, keyword-based search (`rag_system.py`) on a JSON database.
* **Core Logic:** `Python 3.11+`

# Navigate to the project root
cd path/to/rag-poisoning-demo

# Create a virtual environment (e.g., 'rag-env')
python3 -m venv rag-env

# Activate it
source rag-env/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# How to run the demo

* **Terminal 1:** Start the Ollama Server This terminal provides the AI models.
ollama serve
* **Terminal 2:** Run the Streamlit App This terminal runs your user interface.

# Make sure your virtual environment is active
source rag-env/bin/activate

# Run the app.py file
streamlit run app.py


