from google import genai
import os
from dotenv import load_dotenv

load_dotenv()

# Read API key from environment. Do not hard-code secrets in source.
client = genai.Client(
    api_key=os.environ.get("GEMINI_API_KEY")
)

response = client.models.generate_content(
    model="gemini-2.5-flash", contents="write a essay for me in 300 words on LLMs"
)
print(response.text)