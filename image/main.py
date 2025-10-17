from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI()

response = client.chat.completions.create(
    model="gpt-4.1-mini",
    messages=[
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "Generate a 50-word summary for this image."},
                {"type": "image_url", "image_url": {"url": "https://images.unsplash.com/photo-1542037104857-ffbb0b9155fb?ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&q=80&w=1954"}}
            ]
        }
    ]
)

print("Response:", response.choices[0].message.content)