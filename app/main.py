from fastapi import FastAPI


app = FastAPI(
    title="Бронирование Отелей",
    version="0.1.0",
    root_path="/api",
)





@app.get("/")
async def root():
    return {"message": "Привет, мир"}

@app.get("/healthcheck")
async def get_healthcheck():
    return "OK()"