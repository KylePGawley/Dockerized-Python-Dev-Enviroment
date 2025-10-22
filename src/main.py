from fastapi import FastAPI
import redis
import debugpy
import pydantic import BaseModel

app = FastAPI()
r = redis.Redis(host="redis", port=6379, decode_responses=True)

debugpy.listen(("0.0.0.0", 5678))

class TodoCreate(BaseModel):
    title: str

@app.get("/")
def read_root():
    return{"Hello": "Kyle"}

@app.get("/hits")
def read_hits():
    r.incr("hits")
    return{"Number of Hits": r.get("hits")}

@app.get("/todos")
def get_all_todos():
    todos = []

    keys = r.keys("todo:*")

    for key in keys:
        todo_data = r.hgetall(key)
        todo_id = key.split(":")[1]
        todo_data["id"] = todo_id
        todos.append(todo_data)
    return {"todos": todos}

@app.post("/todos")
def create_todo(todo: TodoCreate):
     todo_id = r.incr("todo_counter")
    
    r.hset(
        f"todo:{todo_id}",
        mapping={
            "title": todo.title,
            "completed": "false"
        }
    )
    
    return {
        "message": "Todo created successfully",
        "id": todo_id,
        "title": todo.title
    }