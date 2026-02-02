from flask import Flask, request, jsonify, send_from_directory
import time
import threading
from viotp import request_number, get_otp   # giữ nguyên theo code bạn

app = Flask(__name__)

# LƯU TRẠNG THÁI OTP
otp_sessions = {}

# =============================
# REQUEST OTP
# =============================
@app.route("/request-otp", methods=["POST"])
def request_otp():
    service = request.json.get("service")

    data = request_number(service)
    if not data or "request_id" not in data:
        return jsonify({"error": "Không lấy được số"}), 400

    request_id = data["request_id"]

    otp_sessions[request_id] = {
        "status": "waiting",
        "otp": None,
        "created_at": time.time()
    }

    return jsonify({
        "request_id": request_id,
        "phone": data.get("phone")
    })


# =============================
# CHECK OTP STATUS (CHỐNG RELOAD MẤT DATA)
# =============================
@app.route("/otp-status", methods=["GET"])
def otp_status():
    request_id = request.args.get("request_id")
    session = otp_sessions.get(request_id)

    if not session:
        return jsonify({"status": "expired"})

    return jsonify({
        "status": session["status"],
        "otp": session["otp"]
    })


# =============================
# BACKGROUND CHECK OTP
# =============================
def otp_worker():
    while True:
        for req_id, session in list(otp_sessions.items()):
            if session["status"] == "waiting":
                otp = get_otp(req_id)
                if otp:
                    session["otp"] = otp
                    session["status"] = "done"

            # AUTO EXPIRE SAU 10 PHÚT
            if time.time() - session["created_at"] > 600:
                otp_sessions.pop(req_id, None)

        time.sleep(3)

threading.Thread(target=otp_worker, daemon=True).start()


# =============================
# STATIC FILE
# =============================
@app.route("/")
def index():
    return send_from_directory("static", "index.html")


if __name__ == "__main__":
    app.run(debug=True)
