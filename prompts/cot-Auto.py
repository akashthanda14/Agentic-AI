# Import required libraries
import json                           # For converting between Python dicts and JSON strings
from dotenv import load_dotenv        # To load environment variables (like API keys) from a .env file
from openai import OpenAI             # Main OpenAI Python SDK class

# Load environment variables from the .env file into Python's environment
load_dotenv()

# Create an OpenAI client instance to connect to the API
# ⚠️ Normally, you should use `api_key=os.getenv("OPENAI_API_KEY")`
# to keep your key secret, but here it’s hardcoded (not recommended in production)
Client = OpenAI(
    
    # base_url="https://generativelanguage.googleapis.com/v1beta/"  # optional base URL (commented out)
)

# Define a system-level instruction (prompt) for the model.
# This sets the “personality” and behavior rules of the assistant.
SYSTEM_PROMPT = """

You're an expert AI Assistant in resolving user queries using chain of thought.
You work on START, PLAN and OUTPUT steps.
You need to first PLAN what needs to be done. The PLAN can be multiple steps.
Once you think enough PLAN has been done, finally you can give an OUTPUT.

Rules:
- Strictly Follow the given JSON output format
- Only run one step at a time.
- The sequence of steps is START (where user gives an input), PLAN (That can be multiple times) and finally OUTPUT (which is going to be displayed to the user).

Output JSON Format:
{ "step": "START" | "PLAN" | "OUTPUT", "content": "string" }

Example:
START: Hey, Can you solve 2 + 3 * 5 / 10
PLAN: { "step": "PLAN", "content": "Seems like user is interested in math problem" }
PLAN: { "step": "PLAN", "content": "looking at the problem, we should solve this using BODMAS method" }
PLAN: { "step": "PLAN", "content": "Yes, The BODMAS is correct thing to done here" }
PLAN: { "step": "PLAN", "content": "first we must multiply 3 * 5 which is 15" }
PLAN: { "step": "PLAN", "content": "Now the new equation is 2 + 15 / 10" }
PLAN: { "step": "PLAN", "content": "We must perform divide that is 15 / 10 = 1.5" }
PLAN: { "step": "PLAN", "content": "Now the new equation is 2 + 1.5" }
PLAN: { "step": "PLAN", "content": "Now finally lets perform the add 3.5" }
PLAN: { "step": "PLAN", "content": "Great, we have solved and finally left with 3.5 as ans" }
OUTPUT: { "step": "OUTPUT", "content": "3.5" }

"""

# Print empty lines for readability in terminal
print("\n\n\n")

# Initialize message history for the chat
# The system prompt goes first — this defines how the model should behave.
message_history = [
    {"role": "system", "content": SYSTEM_PROMPT}
]

# Take user input (the first message to start the conversation)
user_query = input("Type here : ")

# Append the user message to the conversation history
message_history.append({"role": "user", "content": user_query})

# Infinite loop — continues generating responses until the model outputs the final "OUTPUT" step
while True:
    # Create a chat completion (i.e., send all previous messages to the model)
    # The model responds with a JSON-formatted message
    response = Client.chat.completions.create(
        response_format={"type": "json_object"},  # Force the model to return valid JSON
        model="gpt-4o-mini",                      # Model name (you can change it to gpt-4o)
        messages=message_history                  # Full chat history so far
    )

    # Extract the model’s raw JSON string output (as text)
    raw_result = response.choices[0].message.content

    # Save model's response to message history (helps continue multi-turn conversation)
    message_history.append({"role": "assistant", "content": raw_result})

    # Convert the model's JSON string into a Python dictionary for easy access
    parsed_result = json.loads(raw_result)

    # Handle the model's structured output depending on the step type
    if parsed_result.get("step") == "START":
        # The model acknowledges the start of the conversation
        print("fire ", parsed_result.get("content"))
        continue  # Continue the loop for the next step

    if parsed_result.get("step") == "PLAN":
        # The model explains its thought process or next planned step
        print("Brain ", parsed_result.get("content"))
        continue  # Keep planning until we get the final OUTPUT

    if parsed_result.get("step") == "OUTPUT":
        # The final step — the actual answer or result
        print("Bot ", parsed_result.get("content"))
        break  # Stop the loop — process finished

# -------------------------------
# The following commented-out section shows a *static example*
# of how you could directly test the logic without the input loop.
# -------------------------------

# USER_PROMPT = "Write a code in Javascript to print n numbers"

# response = Client.chat.completions.create(
#     response_format={"type":"json_object"},
#     model="gpt-4o-mini",
#     messages=[
#         {"role":"user", "content": USER_PROMPT},
#         {"role":"system", "content": SYSTEM_PROMPT},
#         {"role":"assistant", "content": json.dumps({
#              "step": "START",
#              "content": "Write a code in Javascript to print n numbers"
#         })},
#         {"role":"assistant", "content": json.dumps({
#              "step": "PLAN",
#              "content": "The user wants a Javascript function to print 'n' numbers. I will define a function that takes 'n' as an argument and uses a 'for' loop to iterate from 1 to 'n', printing each number using 'console.log'."
#         })},
#         {"role":"assistant", "content": json.dumps({
#             "step": "PLAN",
#             "content": "First, I'll consider how to handle the input 'n'. It should be a positive integer. If 'n' is not a number or is less than 1, the function should handle these edge cases gracefully, perhaps by printing an error message or doing nothing."
#         })},
#         {"role":"assistant", "content": json.dumps({
#            "step": "PLAN",
#            "content": "Now, I will write the Javascript code for the function. It will include the input validation and the loop to print numbers."
#         })}
#     ]
# )

# # Prints the final response (content returned from the model)
# print(response.choices[0].message.content)
