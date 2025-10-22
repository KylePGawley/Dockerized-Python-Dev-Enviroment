from fastapi import FastAPI
import redis

app = FastAPI()

r = redis.Redis(host="redis", port=6379)

import debugpy
debugpy.listen(("0.0.0.0", 5678))

@app.get("/")
def read_root():
    return{"Hello": "Kyle"}

@app.get("/hits")
def read_hits():
    r.incr("hits")
    return{"Number of Hits": r.get("hits")}