import json
import requests


def audit_financial_text(raw_text):
  prompt = f"""You are SpendVault AI, an on-device privacy-first financial auditor.
Parse the following financial transaction text into structured JSON.

Rules:
1. "total_amount" MUST be a float number (e.g. 4999.00, not "4999.00").
2. "anomaly_flag" MUST be true if the merchant contains "UNKNOWN", if it is an unexpected auto-debit, or if the amount is unusually high. Otherwise false.
3. Return ONLY valid JSON, with no markdown formatting or extra text.

Return JSON with these exact keys:
- "merchant_name": string
- "total_amount": float
- "transaction_date": string
- "category": string
- "payment_mode": string
- "anomaly_flag": boolean
- "audit_reason": string

Raw Transaction Text: "{raw_text}"
JSON Output:"""

  response = requests.post(
      "http://localhost:11434/api/generate",
      json={
          "model": "llama3.2:1b",
          "prompt": prompt,
          "stream": False,
          "format": "json",  # Enforces valid JSON from Ollama
      },
  )

  return response.json().get("response", "")


if __name__ == "__main__":
  test_samples = [
      "Paid Rs 1,450.00 to D-Mart Store Rajahmundry on 12-09-2026 via UPI Ref"
      " No 948102.",
      "ALERT: Auto-debit of Rs 4,999.00 to UNKNOWN_SUBSCRIPTION_RENEWAL on"
      " 11-09-2026.",
  ]

  print("=" * 60)
  print(" SpendVault AI - On-Device Local LLM Auditor Test Engine")
  print("=" * 60)

  for idx, sample in enumerate(test_samples, 1):
    print(f"\n--- Sample {idx} ---")
    print(f"Raw Input: {sample}")
    print("Auditing locally on-device...")
    result = audit_financial_text(sample)
    print("Local LLM Result JSON:")
    print(result)