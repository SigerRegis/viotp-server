let pollingInterval = null;

// =======================
// REQUEST OTP
// =======================
async function requestOTP(service) {
  const res = await fetch("/request-otp", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ service })
  });

  const data = await res.json();

  if (!data.request_id) {
    alert("Không lấy được OTP");
    return;
  }

  localStorage.setItem("otp_request_id", data.request_id);
  startPolling(data.request_id);
}

// =======================
// POLLING OTP
// =======================
function startPolling(requestId) {
  if (pollingInterval) clearInterval(pollingInterval);

  pollingInterval = setInterval(async () => {
    const res = await fetch(`/otp-status?request_id=${requestId}`);
    const data = await res.json();

    if (data.status === "done") {
      document.getElementById("otp").innerText = data.otp;
      localStorage.removeItem("otp_request_id");
      clearInterval(pollingInterval);
    }
  }, 3000);
}

// =======================
// AUTO RESUME KHI RELOAD
// =======================
window.onload = () => {
  const savedRequestId = localStorage.getItem("otp_request_id");
  if (savedRequestId) {
    startPolling(savedRequestId);
  }
};
