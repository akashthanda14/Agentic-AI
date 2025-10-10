from google import genai

# The client gets the API key from the environment variable `GEMINI_API_KEY`.
client = genai.Client(
    api_key="***REMOVED***"
)

response = client.models.generate_content(
    model="gemini-2.5-flash", contents="write a essay for me in 300 words on LLMs"
)
print(response.text)