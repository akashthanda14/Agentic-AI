from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

Client = OpenAI(
    api_key="***REMOVED***",
    base_url="https://generativelanguage.googleapis.com/v1beta/"
)
# Few short prompting instructions to the model
SYSTEM_PROMPT="""

You will be ans only and only coding ques and if user ask some other things then ans. Do not ans anything 

Rule:
-Strictly follow the output in JSON format

Output Format:
{{
    "code":"string"or"null",
    "isCodingQues":boolean   
}}

Examples:
Q : Can youn explain the a+b whole square?
A : {{ "code":null , "isCodingQuestion": false}}

Q : Write a code in python for adding two numbers
A : A : {{ "code":def add(a,b):
return a + b , "isCodingQuestion": false}}
      

"""

USER_PROMPT="Write a code in python for adding two numbers"


response = Client.chat.completions.create(
    model="gemini-2.5-flash",
    messages=[
        {"role":"user" , "content":USER_PROMPT },
        {"role":"system" , "content" : SYSTEM_PROMPT}
    ]
)

print(response.choices[0].message.content)
