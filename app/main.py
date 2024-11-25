from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
from app import crud, models, schemas, database, auth
from app.database import get_db

app = FastAPI()

# Initialize the database
models.Base.metadata.create_all(bind=database.engine)

# CORS middleware for allowing front-end interaction
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Include React's URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Register routes for user authentication and task management
@app.post("/register", response_model=schemas.User)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    existing_user = crud.get_user_by_username(db, username=user.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Username already registered"
        )
    hashed_password = auth.get_password_hash(user.password)
    return crud.create_user(db=db, user=user, hashed_password=hashed_password)

@app.post("/login")
def login(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_username(db, username=user.username)
    if not db_user or not auth.verify_password(user.password, db_user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    access_token = auth.create_access_token(data={"sub": db_user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/tasks", response_model=list[schemas.Task])
def get_tasks(
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(auth.verify_token),  # This ensures the user is authenticated
):
    # Fetch tasks associated with the current user
    tasks = crud.get_tasks_by_user(db=db, user_id=current_user.id)  # Assuming `current_user.id` exists
    return tasks


@app.post("/tasks", response_model=schemas.Task)
def create_task(
    task: schemas.TaskCreate,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(auth.verify_token),
):
    return crud.create_task(db=db, task=task, user_id=current_user.id)


@app.put("/tasks/{task_id}", response_model=schemas.Task)
def update_task(
    task_id: int,
    task_update: schemas.TaskUpdate,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(auth.verify_token),
):
    return crud.update_task(db=db, task_id=task_id, task_update=task_update)

@app.delete("/tasks/{task_id}")
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(auth.verify_token),
):
    crud.delete_task(db=db, task_id=task_id)
    return {"message": "Task deleted"}
