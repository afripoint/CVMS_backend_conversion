import requests
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

BASE_URL = "https://v3.api.termii.com"
API_KEY = "TLPZxnJcbCMnoqObvCBxoshLvdaroautmPEHuHixHhdSuclhSpQusErxtjakdV"


def send_message(recipient_number, otp):
    url = f"{BASE_URL}/api/sms/send"

    if not recipient_number:
        return {"success": False, "error": "Recipient number is required"}

    payload = {
        "to": recipient_number,
        "from": "CVMS TEAM",
        "sms": f"Hi, your verification OTP is: {otp}. Do not share this code ",
        "type": "plain",
        "channel": "generic",
        "api_key": API_KEY,
    }
    headers = {
        "Content-Type": "application/json",
    }

    try:
        logging.info(f"Sending OTP to {recipient_number}")
        response = requests.post(url, headers=headers, json=payload, timeout=10)

        response.raise_for_status()

        data = response.json()

        if response.status_code == 200 and "pinId" in data:
            return {"success": True, "message": "OTP sent successfully", "data": data}

        return {"success": False, "error": data.get("message", "Failed to send OTP")}

    # except Exception as e:
    #     return {"success": False, "error": e}

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
