from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import redis
import debugpy
from pydantic import BaseModel
import os
from pathlib import Path

app = FastAPI()
r = redis.Redis(host="redis", port=6379, decode_responses=True)

# Create directory for HTML files if it doesn't exist
HTML_FILES_DIR = Path("src/html_files")
HTML_FILES_DIR.mkdir(exist_ok=True)

app.mount("/static", StaticFiles(directory="src/static"), name="static")
# Mount html_files directory so we can view them in browser
app.mount("/html_files", StaticFiles(directory="src/html_files"), name="html_files")

debugpy.listen(("0.0.0.0", 5678))

class TodoCreate(BaseModel):
    title: str

class HTMLFileCreate(BaseModel):
    filename: str
    content: str

class HTMLFileUpdate(BaseModel):
    content: str

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

# HTML Editor Endpoints

@app.get("/editor")
def html_editor():
    """Serve the HTML editor interface"""
    return FileResponse("src/static/editor.html")

@app.get("/api/html-files")
def list_html_files():
    """List all HTML files in the html_files directory"""
    try:
        files = []
        for file_path in HTML_FILES_DIR.glob("*.html"):
            files.append({
                "filename": file_path.name,
                "size": file_path.stat().st_size,
                "modified": file_path.stat().st_mtime
            })
        return {"files": sorted(files, key=lambda x: x["filename"])}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/html-files/{filename}")
def get_html_file(filename: str):
    """Get the content of a specific HTML file"""
    # Security: Prevent directory traversal attacks
    if ".." in filename or "/" in filename:
        raise HTTPException(status_code=400, detail="Invalid filename")

    file_path = HTML_FILES_DIR / filename

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")

    try:
        content = file_path.read_text(encoding="utf-8")
        return {
            "filename": filename,
            "content": content
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/html-files")
def create_html_file(file_data: HTMLFileCreate):
    """Create a new HTML file"""
    # Security: Prevent directory traversal attacks
    if ".." in file_data.filename or "/" in file_data.filename:
        raise HTTPException(status_code=400, detail="Invalid filename")

    # Ensure filename ends with .html
    if not file_data.filename.endswith(".html"):
        file_data.filename += ".html"

    file_path = HTML_FILES_DIR / file_data.filename

    # Check if file already exists
    if file_path.exists():
        raise HTTPException(status_code=409, detail="File already exists")

    try:
        file_path.write_text(file_data.content, encoding="utf-8")
        return {
            "message": "File created successfully",
            "filename": file_data.filename
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/html-files/{filename}")
def update_html_file(filename: str, file_data: HTMLFileUpdate):
    """Update an existing HTML file"""
    # Security: Prevent directory traversal attacks
    if ".." in filename or "/" in filename:
        raise HTTPException(status_code=400, detail="Invalid filename")

    file_path = HTML_FILES_DIR / filename

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")

    try:
        file_path.write_text(file_data.content, encoding="utf-8")
        return {
            "message": "File updated successfully",
            "filename": filename
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/html-files/{filename}")
def delete_html_file(filename: str):
    """Delete an HTML file"""
    # Security: Prevent directory traversal attacks
    if ".." in filename or "/" in filename:
        raise HTTPException(status_code=400, detail="Invalid filename")

    file_path = HTML_FILES_DIR / filename

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")

    try:
        file_path.unlink()
        return {
            "message": "File deleted successfully",
            "filename": filename
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))