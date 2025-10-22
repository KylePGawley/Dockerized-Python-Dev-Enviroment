from fastapi import FastAPI
import redis

app = FastAPI()

r = redis.Redis(host="redis", port=6379, decode_responses=True)

import debugpy
debugpy.listen(("0.0.0.0", 5678))

@app.get("/")
def read_root():
    return{"Hello": "Kyle"}

@app.get("/hits")
def read_hits():
    r.incr("hits")
    return{"Number of Hits": r.get("hits")}

@app.get("/todo")
def to_do():
    tasks = []
    while True:
        print("\n==== To-Do List ====")
        print("1. Add Tasks")
        print("2. Show Tasks")
        print("3. Mark Tasks as Done")
        print("4. Exit")

        Choice = input("Enter your choice: ")
    if choice == '1':
            print()
            n_tasks = int(input("How may task you want to add: "))
            
            for i in range(n_tasks):
                task = input("Enter the task: ")
                tasks.append({"task": task, "done": False})
                print("Task added!")
    elif choice == '2':
            print("\nTasks:")
            for index, task in enumerate(tasks):
                status = "Done" if task["done"] else "Not Done"
                print(f"{index + 1}. {task['task']} - {status}")
    elif choice == '3':
            task_index = int(input("Enter the task number to mark as done: ")) - 1
            if 0 <= task_index < len(tasks):
                tasks[task_index]["done"] = True
                print("Task marked as done!")
            else:
                print("Invalid task number.")
    elif choice == '4':
     print("Exiting the To-Do List.")
     break

    else:
     print("Invalid choice. Please try again.")

