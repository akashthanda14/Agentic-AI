from openai import OpenAI
from dotenv import load_dotenv
import requests

load_dotenv()

client = OpenAI()

def get_weather(city: str):
    url = f"https://wttr.in/%7B{city.lower()}%7D?format=%25C+%25t"
    response = requests.get(url)

    if response.status_code == 200:
        return f"The Weather in {city} is {response.text}"
    
    return "Something Went Wrong"

def main():
    user_query = input("> ")
    response=client.chat.completions.create(
    model = "gpt-4o",
    messages=[
        {"role":"user" , "content":user_query}
    ]
)
    
    print(f"bot: {response.choices[0].message.content}")

print(get_weather("Phillaur"))