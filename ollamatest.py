from ollama import chat
import json

operator_comment = "Strong vibration started after mold change."

response = chat(
    model="llama3.2:3b",
    messages=[
        {
            "role": "system",
            "content": """
You are an industrial maintenance assistant for injection molding machines.

Analyze operator comments and return ONLY valid JSON.

Use these categories only:
Mechanical
Electrical
Process
Quality
Tooling
Unknown

Use these severity levels only:
LOW
MEDIUM
HIGH

Consider words such as strong vibration, leakage, overheating,
abnormal noise, pressure instability, blockage, and machine stop
as potentially important.

possible_cause must be a short technical hypothesis,
not just a repetition of the operator comment.
"""
        },
        {
            "role": "user",
            "content": f"""
Operator comment:
{operator_comment}

Return exactly:
{{
  "category": "...",
  "severity": "...",
  "possible_cause": "..."
}}
"""
        }
    ],
    format="json"
)

result = json.loads(response["message"]["content"])

print(result)
print("Category:", result["category"])
print("Severity:", result["severity"])
print("Possible Cause:", result["possible_cause"])