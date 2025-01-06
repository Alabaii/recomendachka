from fastapi import FastAPI
from app.users.router import router as router_users

app = FastAPI(
    title="Бронирование Отелей",
    version="0.1.0",
    root_path="/api",
)


app.include_router(router_users)


@app.get("/")
async def root():
    return {"message": "Привет, мир"}

@app.get("/healthcheck")
async def get_healthcheck():
    return "OK()"