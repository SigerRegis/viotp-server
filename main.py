from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
import time
import threading
import secrets

from viotp import request_number, get_otp

app = FastAPI()

# ================= CONFIG =================
PASSWORD = "3333"
SESSIONS = {}  # token -> created_time
SESSION_EXPIRE = 3600  # 1 tiếng

# ================= STATIC =================
app.mount("/static", StaticFiles(directory="static"), name="static")

# ================= OTP STORAGE =================
otp_sessions = {}

# ================= AUTH UTILS =================
def is_authenticated(request: Request):
    token = request.cookies.get("auth_token")
    if not token:
        return False
    created = SESSIONS.get(token)
    if not created:
        return False
    if time.time() - created > SESSION_EXPIRE:
        SESSIONS.pop(token, None)
        return False
    return True

# ================= MIDDLEWARE =================
@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    path = request.url.path

    # Cho phép login
    if path.startswith("/login") or path.startswith("/static"):
        return await call_next(request)

    # Chặn toàn bộ API + trang chủ
    if path.startswith("/api") or path == "/":
        if not is_authenticated(request):
            if path.startswith("/api"):
                return JSONResponse(
                    {"error": "Unauthorized"}, status_code=401
                )
            return RedirectResponse("/login")

    return await call_next(request)

# ================= LOGIN PAGE =================
@app.get("/login", response_class=HTMLResponse)
def login_page():
    return """
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>Login</title>
<style>
body { font-family: Arial; max-width: 300px; margin: 100px auto; }
input, button { width: 100%; padding: 12px; margin-top: 10px; }
</style>
</head>
<body>
<h3>🔐 Nhập mật khẩu</h3>
<input type="password" id="pw" placeholder="Mật khẩu">
<button onclick="login()">Đăng nhập</button>
<p id="msg"></p>

<script>
async function login() {
  const pw = document.getElementById("pw").value;
  const res = await fetch("/login", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({password: pw})
  });
  if (res.ok) location.href = "/";
  else document.getElementById("msg").innerText = "❌ Sai mật khẩu";
}
</script>
</body>
</html>
"""

@app.post("/login")
def login(data: dict):
    if data.get("password") != PASSWORD:
        return JSONResponse({"error": "wrong"}, status_code=401)

    token = secrets.token_hex(16)
    SESSIONS[token] = time.time()

    res = RedirectResponse("/", status_code=302)
    res.set_cookie(
        "auth_token",
        token,
        httponly=True,
        samesite="lax"
    )
    return res

# ================= ROOT =================
@app.get("/", response_class=HTMLResponse)
def home():
    with open("static/index.html", encoding="utf-8") as f:
        return f.read()

# ================= API =================
@app.post("/api/rent")
def rent(service_id: int):
    return request_number(service_id)

@app.get("/api/otp/{request_id}")
def otp(request_id: str):
    return get_otp(request_id)

@app.get("/api/balance")
def balance():
    return {"data": {"balance": "OK"}}

@app.get("/api/services")
def services():
    return {"data": []}

# ================= OTP WORKER =================
def otp_worker():
    while True:
        time.sleep(5)

threading.Thread(target=otp_worker, daemon=True).start()
