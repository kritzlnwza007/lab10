from litellm import completion
from config import MODEL

messages = [
    {"role": "system", "content": "You ONLY reply with a JSON object."},
    {"role": "user", "content": "Say hi in JSON."}
]

resp = completion(model=MODEL, messages=messages, response_format={"type":"json_object"})
print(resp.choices[0].message["content"])
