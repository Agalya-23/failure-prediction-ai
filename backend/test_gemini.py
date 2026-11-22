import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

api_key = os.environ["GEMINI_API_KEY"]
client = genai.Client(api_key=api_key)

MODEL = os.getenv("GEMINI_MODEL", "gemini-3.1-flash-lite")

print("Testing Gemini API...")
print("Model:", MODEL)

response = client.interactions.create(
    model=MODEL,
    input="Say hello in 5 words"
)

print("SUCCESS!")
print(response.output_text)