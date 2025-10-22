from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import redis
import debugpy
from pydantic import BaseModel

app = FastAPI()
r = redis.Redis(host="redis", port=6379, decode_responses=True)

app.mount("/static", StaticFiles(directory="src/static"), name="static")

debugpy.listen(("0.0.0.0", 5678))

class TodoCreate(BaseModel):
    title: str

@app.get("/")
def read_root():
    return FileResponse("src/static/index.html")

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
@app.put("/todos/{todo_id}/complete")
def mark_complete(todo_id: int):

    if not r.exists(f"todo:{todo_id}"):
        return {"error": "Todo not found"}
    
    r.hset(f"todo:{todo_id}", "completed", "true")
    
    return {
        "message": "Todo marked as complete",
        "id": todo_id
    }
@app.delete("/todos/{todo_id}")
def delete_todo(todo_id: int):
    
    if not r.exists(f"todo:{todo_id}"):
        return {"error": "Todo not found"}
    
    r.delete(f"todo:{todo_id}")
    
    return {
        "message": "Todo deleted successfully",
        "id": todo_id
    }