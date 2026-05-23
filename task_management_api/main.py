import aiosqlite
from fastapi import FastAPI, HTTPException, status, Depends
from typing import List
from schemas import UserCreate, UserResponse, TaskCreate, TaskUpdate, TaskResponse

app = FastAPI(
    title="RESTful Task & User Management API",
    description="A high-performance asynchronous API using FastAPI, Pydantic, and SQLite",
    version="1.0.0"
)

DATABASE_NAME = "management.db"

async def init_db():
    async with aiosqlite.connect(DATABASE_NAME) as db:
        await db.execute("PRAGMA foreign_keys = ON;")
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL
            );
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                status TEXT NOT NULL DEFAULT 'todo',
                user_id INTEGER NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
            );
        """)
        await db.commit()

@app.on_event("startup")
async def startup_event():
    await init_db()

async def get_db():
    async with aiosqlite.connect(DATABASE_NAME) as db:
        await db.execute("PRAGMA foreign_keys = ON;")
        yield db

@app.post("/users/", response_model=UserResponse, status_code=status.HTTP_201_CREATED, tags=["Users"])
async def create_user(user: UserCreate, db: aiosqlite.Connection = Depends(get_db)):
    try:
        cursor = await db.execute("INSERT INTO users (username, email) VALUES (?, ?)", (user.username, user.email))
        await db.commit()
        return {"id": cursor.lastrowid, "username": user.username, "email": user.email}
    except aiosqlite.IntegrityError:
        raise HTTPException(status_code=400, detail="A user with this email already exists.")

@app.get("/users/", response_model=List[UserResponse], tags=["Users"])
async def get_users(db: aiosqlite.Connection = Depends(get_db)):
    async with db.execute("SELECT id, username, email FROM users") as cursor:
        rows = await cursor.fetchall()
        return [{"id": r[0], "username": r[1], "email": r[2]} for r in rows]

@app.post("/tasks/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED, tags=["Tasks"])
async def create_task(task: TaskCreate, db: aiosqlite.Connection = Depends(get_db)):
    try:
        cursor = await db.execute(
            "INSERT INTO tasks (title, description, status, user_id) VALUES (?, ?, ?, ?)",
            (task.title, task.description, task.status.value, task.user_id)
        )
        await db.commit()
        return {"id": cursor.lastrowid, "title": task.title, "description": task.description, "status": task.status, "user_id": task.user_id}
    except aiosqlite.IntegrityError:
        raise HTTPException(status_code=404, detail=f"User with id {task.user_id} does not exist.")

@app.get("/tasks/", response_model=List[TaskResponse], tags=["Tasks"])
async def get_tasks(status_filter: str = None, db: aiosqlite.Connection = Depends(get_db)):
    query = "SELECT id, title, description, status, user_id FROM tasks"
    params = ()
    if status_filter:
        query += " WHERE status = ?"
        params = (status_filter,)
    async with db.execute(query, params) as cursor:
        rows = await cursor.fetchall()
        return [{"id": r[0], "title": r[1], "description": r[2], "status": r[3], "user_id": r[4]} for r in rows]