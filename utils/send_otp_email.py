import requests
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

BASE_URL = "https://v3.api.termii.com"
API_KEY = "TLPZxnJcbCMnoqObvCBxoshLvdaroautmPEHuHixHhdSuclhSpQusErxtjakdV"


def send_otp_email(email_address, otp):
    url = "https://BASE_URL/api/email/otp/send"

    if not email_address:
        return {"success": False, "error": "Recipient email is required"}

    payload = {
        "api_key": API_KEY,
        "email_address": email_address,
        "code": otp,
        "email_configuration_id": "00cfcw93-pc0d-43bc-9f7f-589a3f306ae5",
    }
    headers = {
        "Content-Type": "application/json",
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        response.raise_for_status()

        data = response.json()
        if data.get("pinId"):
            return {"success": True, "message": "OTP sent successfully", "data": data}
        else:
            return {"success": False, "error": data.get("message", "Unknown error")}

    except requests.exceptions.Timeout:
        logging.error("Request timed out")
        return {"success": False, "error": "Request timed out"}

    except requests.exceptions.ConnectionError:
        logging.error("Failed to connect to Termii API")
        return {"success": False, "error": "Failed to connect to Termii API"}

    except requests.exceptions.HTTPError as err:
        logging.error(f"HTTP error: {err}")
        return {"success": False, "error": f"HTTP error: {err}"}

    except requests.exceptions.RequestException as err:
        logging.error(f"Request failed: {err}")
        return {"success": False, "error": "An unexpected error occurred"}
