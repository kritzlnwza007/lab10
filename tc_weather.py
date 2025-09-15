# Part B — Example 2: Weather tool (simulated) with intermediate view
import json
from litellm import completion
from config import MODEL

def get_weather(city: str, unit: str = "celsius"):
    temp_c = 28  # pretend API
    return {"city": city, "unit": unit, "temperature": temp_c if unit == "celsius" else round(temp_c * 9/5 + 32)}

weather_tool = [{
    "name": "get_weather",
    "description": "Get current weather (simulated)",
    "parameters": {
        "type": "object",
        "properties": {
            "city": {"type": "string"},
            "unit": {"type": "string", "enum": ["celsius", "fahrenheit"], "default": "celsius"}
        },
        "required": ["city"]
    }
}]

messages = [{"role": "user", "content": "What’s the weather in Chiang Mai in fahrenheit?"}]
first = completion(model=MODEL, messages=messages, functions=weather_tool, function_call="auto")
msg = first.choices[0].message
fc = getattr(msg, "function_call", None) if hasattr(msg, "function_call") else msg.get("function_call")
print("=== INTERMEDIATE (weather) ===")
print("function name:", getattr(fc, "name", None) if fc else None)
print("arguments:", getattr(fc, "arguments", None) if fc else None)
 
if fc:
    args = json.loads(fc.arguments or "{}")
    tool_result = get_weather(**args)
    messages.append({"role": "assistant", "content": None, "function_call": {"name": fc.name, "arguments": fc.arguments}})
    messages.append({"role": "function", "name": "get_weather", "content": json.dumps(tool_result)})
    final = completion(model=MODEL, messages=messages)
    print("\nFINAL:", final.choices[0].message["content"])
else:
    print("No tool call proposed.")
