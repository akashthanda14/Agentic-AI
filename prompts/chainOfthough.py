import json
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

Client = OpenAI(
    api_key="***REMOVED***",
    base_url="https://generativelanguage.googleapis.com/v1beta/"
)
# Few short prompting instructions to the model
SYSTEM_PROMPT="""

You're an expert AI Assistant in resolving user queries using chain of thought.
You work on START, PLAN and OUPUT steps.
You need to first PLAN what needs to be done. The PLAN can be multiple steps.
Once you think enough PLAN has been done, finally you can give an OUTPUT.

Rules:
- Strictly Follow the given JSON output format
- Only run one step at a time.
- The sequence of steps is START (where user gives an input), PLAN (That can be multiple times) and finally OUTPUT (which is going to the displayed to
the user).


Output JSON Format:
{ "step": "START" | "PLAN" | "OUTPUT", "content": "string" }
Example:
START: Hey, Can you solve 2 + 3 * 5 / 10
PLAN: { "step": "PLAN": "content": "Seems like user is interested in math
problem" }
PLAN: { "step": "PLAN": "content": "looking at the problem, we should solve this using BODMAS method" }
PLAN: { "step": "PLAN": "content": "Yes, The BODMAS is correct thing to done here' }
PLAN: { "step": "PLAN": "content": "first we must multiply 3 * 5 which is
15" }
PLAN: { "step": "PLAN": "content": "Now the new equation is 2 + 15 / 10" }
PLAN: { "step": "PLAN": "content": "We must perform divide that is 15 / 10
= 1.5" }
PLAN: { "step": "PLAN": "content": "Now the new equation is 2 + 1.5" }
PLAN: { "step": "PLAN": "content": "Now finally lets perform the add 3.5" PLAN: { "step": "PLAN": "content": "Great, we have solved and finally left with 3.5 as ans" }
OUTPUT: { "step": "OUTPUT": "content": "3.5" }
      

"""

USER_PROMPT="Write a code in Javascript to print n numbers"


response = Client.chat.completions.create(
    response_format={"type":"json_object"},
    model="gpt-4o-mini",
    messages=[
        {"role":"user" , "content":USER_PROMPT },
        {"role":"system" , "content" : SYSTEM_PROMPT},
        {"role":"assistant" ,"content" : json.dumps({
             "step": "START",
  "content": "Write a code in Javascript to print n numbers"
        })},
        {"role":"assistant" ,"content" : json.dumps({
             "step": "PLAN",
 "content": "The user wants a Javascript function to print 'n' numbers. I will define a function that takes 'n' as an argument and uses a 'for' loop to iterate from 1 to 'n', printing each number using 'console.log'."
        })}, {"role":"assistant" ,"content" : json.dumps({
            "step": "PLAN", "content": "First, I'll consider how to handle the input 'n'. It should be a positive integer. If 'n' is not a number or is less than 1, the function should handle these edge cases gracefully, perhaps by printing an error message or doing nothing."
        })},
         {"role":"assistant" ,"content" : json.dumps({
           "step": "PLAN", "content": "Now, I will write the Javascript code for the function. It will include the input validation and the loop to print numbers." 
        })}


    ]
)

print(response.choices[0].message.content)
