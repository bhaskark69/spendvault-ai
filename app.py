import json
import sys
import requests

def run_local_financial_audit(raw_input_text: str, model_name: str = "llama3.2:1b") -> dict:
    """
    Executes an on-device/local LLM audit on raw financial text (receipts, invoices, or bank SMS).
    Extracts transaction details and flags potential anomaly charges in structured JSON.
    """
    system_prompt = (
        "You are SpendVault AI, an on-device financial auditor LLM running locally. "
        "Analyze the input text and return ONLY a valid JSON object with the following schema:\n"
        "{\n"
        '  "merchant_name": "string",\n'
        '  "total_amount": "number or string",\n'
        '  "transaction_date": "string",\n'
        '  "category": "Groceries | Utilities | Personal | Subscriptions | Business | Uncategorized",\n'
        '  "payment_mode": "UPI | Card | NetBanking | Cash | Unknown",\n'
        '  "anomaly_flag": true or false,\n'
        '  "audit_reason": "string explaining why it is normal or flagged"\n'
        "}\n"
        "Do not include any intro, markdown wrap, or conversational text. Return raw JSON only."
    )

    payload = {
        "model": model_name,
        "prompt": f"{system_prompt}\n\nInput Financial Document:\n{raw_input_text}",
        "stream": False,
        "options": {
            "temperature": 0.1
        }
    }

    try:
        response = requests.post("http://localhost:11434/api/generate", json=payload, timeout=30)
        response.raise_for_status()

        result_text = response.json().get("response", "").strip()

        if result_text.startswith("```json"):
            result_text = result_text[7:]
        if result_text.startswith("```"):
            result_text = result_text[3:]
        if result_text.endswith("```"):
            result_text = result_text[:-3]

        return json.loads(result_text.strip())

    except requests.exceptions.ConnectionError:
        print("[Error] Could not connect to local Ollama engine.")
        print("Make sure Ollama is installed and running (`ollama run llama3.2:1b`).")
        return {}
    except json.JSONDecodeError:
        print("[Warning] Raw output was not strict JSON. Raw text received:")
        print(result_text)
        return {"raw_output": result_text}

if __name__ == "__main__":
    print("==========================================================")
    print(" SpendVault AI - On-Device Local LLM Auditor Test Engine ")
    print("==========================================================\n")

    sample_transactions = [
        "Paid Rs 1,450.00 to D-Mart Store Rajahmundry on 12-09-2026 via UPI Ref No 948102.",
        "ALERT: Auto-debit of Rs 4,999.00 to UNKNOWN_SUBSCRIPTION_RENEWAL on 11-09-2026."
    ]

    for idx, tx in enumerate(sample_transactions, 1):
        print(f"--- Sample {idx} ---")
        print(f"Raw Input: {tx}")
        print("Auditing locally on-device...")

        audit_result = run_local_financial_audit(tx)
        print("Local LLM Result JSON:")
        print(json.dumps(audit_result, indent=2))
        print("\n")
