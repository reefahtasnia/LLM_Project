from openai import OpenAI

# Connect to LM Studio's local API
client = OpenAI(
    base_url="http://127.0.0.1:1234/v1",  # Adjust if needed
    api_key="lm-studio"  # Any string works
)

# Test connection
try:
    response = client.chat.completions.create(
        model="llama-3.2-1b-instruct",  # Must match model name in LM Studio
        messages=[{"role": "user", "content": "Hello, world!"}],
        max_tokens=100
    )
    print("🤖 Response:", response.choices[0].message.content)
except Exception as e:
    print("❌ Error:", str(e))