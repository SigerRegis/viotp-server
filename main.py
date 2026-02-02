from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from viotp import *

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
def home():
    with open("static/index.html", encoding="utf-8") as f:
        return f.read()

@app.get("/api/balance")
def balance():
    return get_balance()

@app.get("/api/services")
def services():
    return get_services()

@app.post("/api/rent")
def rent(service_id: int):
    return rent_sim(service_id)

@app.get("/api/otp/{request_id}")
def otp(request_id: str):
    return get_otp(request_id)
