from litellm import completion
from config import MODEL
import json

messages = [
    {"role": "system", "content": "You ONLY reply with a single JSON object."},
    {"role": "user", "content": "Extract: Sarah Johnson, 28, sj@example.com; likes smartphones and tablets."}
]

resp = completion(
    model=MODEL,
    messages=messages,
    response_format={"type": "json_object"},  # JSON Mode
    max_tokens=200,
)
content = resp.choices[0].message["content"]
print("RAW JSON string:\n", content)
print("\nParsed dict:\n", json.dumps(json.loads(content), indent=2))
