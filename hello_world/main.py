from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

Client = OpenAI(
     api_key=os.environ.get("OPENAI_API_KEY"),
)

response = Client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role":"user" , "content":"what is 223+29829" },
        {"role":"system" , "content" : "You are a Maths Expert and you asnwer only in only maths if user ask something else then say just sorry and do not answer that"}
    ]
)

print(response.choices[0].message.content)
