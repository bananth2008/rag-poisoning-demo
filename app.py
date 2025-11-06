# app.py
"""
RAG Poisoning Demo - v15 (Improved Summary)

Fixes:
- Makes the "Transaction Summary" more subtle and intuitive.
- Clearly shows the "ground truth" account vs. the paid account.
- Sets expander to expanded=True for immediate visibility.
"""

import streamlit as st
from pathlib import Path
import sys
import shutil
import io
from contextlib import redirect_stdout
import time

# --- CORRECTED IMPORT SECTION ---
sys.path.insert(0, str(Path(__file__).parent / "src"))

from agent import PaymentAgent
from rag_system import VendorRAG
# --- END IMPORT FIX ---


# === HELPER FUNCTION (MOVED TO TOP) ===

def setup_environment(scenario):
    """Setup database based on scenario"""
    
    DATA_DIR = Path(__file__).parent / "data"
    CLEAN_DB = DATA_DIR / "vendors_clean.json"
    POISON_DB = DATA_DIR / "vendors_poisoned.json"
    LIVE_DB = DATA_DIR / "vendors.json"
    
    # Reset to clean state
    shutil.copy(CLEAN_DB, LIVE_DB)
    
    # Initialize agent
    use_guardrails = (scenario == 'guarded')
    agent = PaymentAgent(
        use_guardrails=use_guardrails,
        live_db_path=str(LIVE_DB),
        poison_db_path=str(POISON_DB)
    )
    
    # Inject poison if needed
    if scenario in ['poisoned', 'guarded']:
        agent.inject_poison()
    
    return agent


# === PAGE CONFIG & SESSION STATE ===

st.set_page_config(
    page_title="RAG Poisoning Demo",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'scenario' not in st.session_state:
    st.session_state.scenario = 'clean'
    st.session_state.transactions = []
    st.session_state.telemetry_logs = []
    
    log_stream = io.StringIO()
    with redirect_stdout(log_stream):
        st.session_state.agent = setup_environment('clean') # Start clean
    
    log_output = log_stream.getvalue()
    st.session_state.telemetry_logs.append(f"### app.py Log\n```\n{log_output}\n```")


# === MAIN UI ===

st.title("🛡️ RAG Poisoning Attack Demo")
st.markdown("**US Bank AI Security - Payment Agent Vulnerability Demonstration**")

st.divider()

# === LEFT AND RIGHT COLUMNS ===

left_col, right_col = st.columns([1, 1])


# === LEFT SIDE: CONTROLS ===

with left_col:
    st.header("🎮 Demo Controls")
    
    # Scenario selector
    scenario = st.radio(
        "Select Scenario:",
        options=['clean', 'poisoned', 'guarded'],
        format_func=lambda x: {
            'clean': '✅ Act 1: Clean Database (Normal)',
            'poisoned': '🚨 Act 2: Poisoned Database (Attack)',
            'guarded': '🛡️ Act 3: Guarded Database (Defense)'
        }[x],
        key='scenario_selector'
    )
    
    # Setup button
    if st.button("🔄 Setup Environment", type="primary"):
        with st.spinner(f"Setting up '{scenario}' environment..."):
            
            log_stream = io.StringIO()
            with redirect_stdout(log_stream):
                st.session_state.agent = setup_environment(scenario)
                st.session_state.scenario = scenario
                st.session_state.transactions = []
            
            st.session_state.telemetry_logs = []
            log_output = log_stream.getvalue()
            st.session_state.telemetry_logs.append(f"### app.py Log\n```\n{log_output}\n```")
        
        st.success(f"Environment ready: {scenario.upper()}")
        st.rerun() 
    
    st.divider()
    
    # Payment request form
    st.subheader("💰 Payment Request")
    
    vendor_name = st.text_input("Vendor Name:", value="ABC Corp")
    amount = st.number_input("Amount ($):", min_value=0, value=10000, step=1000)
    description = st.text_input("Description:", value="Q4 Invoice")
    
    # Process payment button
    if st.button("💸 Execute Payment", type="primary"):
        
        if st.session_state.agent:
            payment_request = f"Please pay ${amount:,.0f} to {vendor_name} for {description}"
            st.session_state.telemetry_logs.append(f"👤 **User:** {payment_request}")
            st.rerun() 
        else:
            st.error("Agent not initialized. Please set up the environment first.")

    st.divider()
    
    # --- THIS IS THE NEW, MORE INTUITIVE SUMMARY ---
    st.subheader("📊 Transaction Summary")
    
    # Establish the "Ground Truth" for the audience
    KNOWN_GOOD_ACCOUNT = "123456789"
    st.caption(f"Note: The correct, verified account for ABC Corp is **{KNOWN_GOOD_ACCOUNT}**.")

    if st.session_state.transactions:
        # Get the latest transaction (there should only be one)
        txn = st.session_state.transactions[-1] 
        
        with st.expander(f"Transaction #{len(st.session_state.transactions)}: ${txn['amount']:,.2f}", expanded=True):
            st.write(f"**Vendor:** {txn['vendor_name']}")
            st.write(f"**Status:** {txn['status']}")
            
            account_number = txn['account_number']
            
            # Compare the paid account to the known good account
            if account_number == KNOWN_GOOD_ACCOUNT:
                st.write(f"**Paid to Account:** `{account_number}`")
                st.success("✅ **Verified:** Payment sent to the correct account.")
            else:
                # This is the "wow" moment
                st.write(f"**Paid to Account:** `{account_number}`")
                st.error("🚨 **Fraud Alert:** Payment was sent to an **unverified** account!")

    elif st.session_state.scenario == 'guarded' and any("SECURITY BLOCK" in str(log) for log in st.session_state.telemetry_logs):
        st.success("✅ **Attack Blocked!** No transaction was created.")
    else:
        st.info("No transactions yet")
    # --- END OF NEW SUMMARY SECTION ---


# === RIGHT SIDE: TELEMETRY ===

with right_col:
    st.header("📡 System Telemetry")
    
    status_color = {
        'clean': '🟢',
        'poisoned': '🔴',
        'guarded': '🟡'
    }
    
    st.markdown(f"### {status_color.get(st.session_state.scenario, '⚪')} Current Mode: **{st.session_state.scenario.upper()}**")
    
    if st.session_state.agent:
        vendor_count = len(st.session_state.agent.rag.vendors)
        
        names = [v['name'] for v in st.session_state.agent.rag.vendors]
        duplicates = [n for n in set(names) if names.count(n) > 1]
        
        st.metric("Vendors in Database", vendor_count)
        
        if duplicates:
            st.warning(f"⚠️ Duplicate vendors detected: {', '.join(duplicates)}")
        else:
            st.success("✅ No duplicate vendors")
        
        if st.session_state.agent.use_guardrails:
            st.success("🛡️ Guardrails: ACTIVE")
        else:
            st.error("⚠️ Guardrails: DISABLED")
    
    st.divider()
    
    st.subheader("📜 Activity Log")
    log_container = st.container(height=400)
    
    with log_container:
        if st.session_state.telemetry_logs:
            for log in st.session_state.telemetry_logs:
                if isinstance(log, str): 
                    if log.startswith("👤"):
                        st.info(log)
                    elif log.startswith("🤖"):
                        st.success(log)
                    else:
                        st.markdown(log, unsafe_allow_html=True) 
        else:
            st.write("*No activity yet. Execute a payment to see logs.*")
    
    st.divider()
    
    # --- This section was removed to simplify the UI ---
    
    # --- STREAMING LOGIC ---
    if st.session_state.telemetry_logs:
        last_log = st.session_state.telemetry_logs[-1]
        if isinstance(last_log, str) and last_log.startswith("👤 **User:**"):
            
            payment_request = last_log.replace("👤 **User:**", "").strip()
            
            with log_container:
                with st.empty():
                    log_buffer = ""
                    final_response = ""
                    for log_line in st.session_state.agent.process_request(payment_request):
                        log_buffer += log_line + "\n"
                        st.markdown(f"```\n{log_buffer}\n```")
                        final_response = log_line 
                        time.sleep(0.1) 
                    
                    if final_response:
                        final_response = final_response.split("🤖 Agent (Final Response):")[-1].strip().split("=")[0].strip()
                    else:
                        final_response = "Agent did not provide a final response."
                    
                    st.session_state.telemetry_logs.append(f"### agent.py Log (Full Telemetry)\n```\n{log_buffer}\n```")
                    st.session_state.telemetry_logs.append(f"🤖 **Agent:** {final_response}")
                    
                    st.session_state.transactions = st.session_state.agent.get_transactions()
                    
                    st.rerun()


# === SIDEBAR: EXPLANATION ===
with st.sidebar:
    st.header("ℹ️ About This Demo")
    
    st.markdown("""
    ### RAG Poisoning Attack
    
    This demo shows how an attacker can poison
    a RAG (Retrieval Augmented Generation) system
    to redirect payments to their accounts.
    
    ---
    
    ### Scenarios:
    
    **✅ Act 1: Clean Database**
    - Normal operation. Agent finds the correct vendor and pays the correct account.
    
    **🚨 Act 2: Poisoned Database**
    - An attacker has injected a fake record for "ABC Corp" with *their* bank account.
    - The AI finds the poisoned data first and processes the payment to the **attacker**.
    
    **🛡️ Act 3: Guarded**
    - The database is poisoned, but the Guardrail is ON.
    - The Guardrail inspects the data *before* the AI uses it.
    - It detects the malicious instructions in the "notes" field and **blocks the attack**.
    
    ---
    
    ### How It Works:
    
    1. **RAG Search**: Agent searches for "ABC Corp".
    2. **Vulnerability**: The poisoned record is found first.
    3. **Attack (Act 2)**: The AI trusts the poisoned data and pays the wrong account.
    4. **Defense (Act 3)**: An AI "Judge" model inspects the data, finds the malicious text, and stops the transaction.
    """)
    
    st.divider()
    
    st.caption("** AI Security Team**")
    st.caption("January 2025")


# === FOOTER ===
st.divider()

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Total Transactions", len(st.session_state.transactions))

with col2:
    if st.session_state.transactions:
        total_amount = sum(t['amount'] for t in st.session_state.transactions)
        st.metric("Total Amount", f"${total_amount:,.0f}")

with col3:
    if st.session_state.scenario == 'poisoned' and st.session_state.transactions:
        poisoned_count = sum(1 for t in st.session_state.transactions if t['account_number'] == '999999999')
        if poisoned_count > 0:
            st.metric("Poisoned Payments", poisoned_count, delta=f"-${sum(t['amount'] for t in st.session_state.transactions if t['account_number'] == '999999999'):,.0f}", delta_color="inverse")
    elif st.session_state.scenario == 'guarded' and not st.session_state.transactions:
         st.metric("Poisoned Payments", 0, delta="Attack Blocked", delta_color="off")