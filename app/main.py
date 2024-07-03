from fastapi import FastAPI

app = FastAPI()

@app.get("/isalive")
async def is_alive():
    return {"status": "alive"}