from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

Client = OpenAI(
    api_key="***REMOVED***",
    base_url="https://generativelanguage.googleapis.com/v1beta/"
)
# directly giving instructions to the model
SYSTEM_PROMPT="You will be ans only and only coding ques and if user ask some other things then ans. Do not ans anything "

response = Client.chat.completions.create(
    model="gemini-2.5-flash",
    messages=[
        {"role":"user" , "content":SYSTEM_PROMPT },
        {"role":"system" , "content" : "Please explain python programming"}
    ]
)

print(response.choices[0].message.content)
