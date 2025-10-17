from redis import Redis
from rq import Queue

# Use an explicit queue name so workers listening on the same queue pick up jobs.
QUEUE_NAME = "rag_queue.queue.worker"

queue = Queue(name=QUEUE_NAME, connection=Redis(host="localhost", port=6379))


