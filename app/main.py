from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database.database import engine, Base, get_db

# FastAPI app
app = FastAPI(
    title="Drug Prevention API",
    description="API for Drug Prevention Application with Recommendation System",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import các models (sau khi đã tạo)
# from app.models import *

# Include routers
from app.routes.recommendation_routes import router as recommendation_router
from app.routes.recognize_toxic_chat import router as toxic_chat_router

app.include_router(recommendation_router)
app.include_router(toxic_chat_router)

@app.get("/")
def read_root():
    return {"message": "Hello, PostgreSQL with SQLAlchemy!"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)