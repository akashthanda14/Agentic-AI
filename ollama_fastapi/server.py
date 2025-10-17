from fastapi import FastAPI , Body
from ollama import Client

client = Client(
    host="http://localhost:11434"
)

app=FastAPI()

@app.get("/")
def read_root():
    return {"hello":"World"}

@app.post("/chat")
def chat(
        message: str = Body(..., descripition="The Message")
):
    response = client.chat(model="gemma:2b" , messages=[
        {"role":"user" , "content":message}

    ])
    return {"response": response.message.content }