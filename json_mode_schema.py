from litellm import completion
from config import MODEL
import json

schema = {
  "name": "UserInfo",
  "schema": {
    "type": "object",
    "properties": {
      "name": {"type": "string"},
      "email": {"type": "string"},
      "age": {"type": "integer"},
      "preferences": {"type": "array", "items": {"type": "string"}}
    },
    "required": ["name", "email"],
    "additionalProperties": False
  },
  "strict": True
}

messages = [
  {"role": "system", "content": "Return ONLY a JSON object matching the schema."},
  {"role": "user", "content": "Extract: Sarah Johnson, 28, sj@example.com; likes smartphones and tablets."}
]

resp = completion(
  model=MODEL,
  messages=messages,
  response_format={"type": "json_schema", "json_schema": schema},
)
content = resp.choices[0].message["content"]
print("RAW JSON:\n", content)
print("\nParsed:\n", json.dumps(json.loads(content), indent=2))
