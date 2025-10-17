from dotenv import load_dotenv
load_dotenv()
from fastapi import FastAPI,Query
from .client.rq_client import queue
from .queue.worker import process_query

app=FastAPI()


@app.get("/")
def read_root():
    return {"status": "Server is up and running"}

@app.post("/chat")
def chat(
        query:str = Query(
            ...,
            title="Query",
            description="User query to be processed",
            example="What is RAG?"
        )
):
    job = queue.enqueue(process_query, query)
    return {"status": "queued", "job_id": job.id}

@app.get("/job-status")
def result(
        job_id: str = Query(...,description="Job ID")
):
    job = queue.fetch_job(job_id=job_id)
    result = job.return_value()

    return { "result": result}