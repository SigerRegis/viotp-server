from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse, Response, FileResponse
import secrets, time, os

app = FastAPI()

# ===== CONFIG =====
PASSWORD = "3333"
SESSIONS = {}

# ===== AUTH =====
def is_auth(request: Request):
    token = request.cookies.get("auth")
    return token in SESSIONS

# ===== MIDDLEWARE =====
@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    path = request.url.path

    # Cho phép login
    if path == "/login":
        return await call_next(request)

    # Sai auth → TRẢ TRANG TRẮNG
    if not is_auth(request):
        if path.startswith("/api"):
            return Response(status_code=403)
        return Response(status_code=403)  # trắng tinh

    return await call_next(request)

# ===== LOGIN PAGE =====
@app.get("/login", response_class=HTMLResponse)
def login_page():
    return """
<!DOCTYPE html>
<html>
<body>
<input type="password" id="pw">
<button onclick="login()">OK</button>

<script>
async function login() {
  const pw = document.getElementById("pw").value;
  const res = await fetch("/login", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({password: pw})
  });
  if (res.ok) location.href = "/";
}
</script>
</body>
</html>
"""

@app.post("/login")
def login(data: dict):
    if data.get("password") != PASSWORD:
        return Response(status_code=403)  # SAI → TRẮNG

    token = secrets.token_hex(16)
    SESSIONS[token] = time.time()

    res = Response(status_code=200)
    res.set_cookie("auth", token, httponly=True)
    return res

# ===== ROOT =====
@app.get("/", response_class=HTMLResponse)
def home():
    return open("static/index.html", encoding="utf-8").read()

# ===== STATIC (CÓ AUTH) =====
@app.get("/static/{path:path}")
def static_files(path: str):
    return FileResponse(os.path.join("static", path))

# ===== API =====
@app.get("/api/balance")
def balance():
    return {"ok": True}
