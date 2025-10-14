from redis import redis 
from rq import Queue

queue = Queue(connection=redis.Redis(
    host='valkey',
    port=6379
))

