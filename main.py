from fastapi import FastAPI
from app.routers import librarian_router, auth_router, reader_router, book_router

app = FastAPI()

app.include_router(librarian_router.router)
app.include_router(auth_router.router)
app.include_router(reader_router.router)
app.include_router(book_router.router)

@app.get("/")
def root():
    return {"message": "Welcome"}
