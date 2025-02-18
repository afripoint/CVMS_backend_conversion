import requests

import logging

# Configure logging
logging.basicConfig(level=logging.INFO)


BASE_URL = "https://v3.api.termii.com"
API_KEY = "TLPZxnJcbCMnoqObvCBxoshLvdaroautmPEHuHixHhdSuclhSpQusErxtjakdV"


def verify_otp(pin_id, pin):
    url = f"{BASE_URL}/api/sms/otp/verify"
    payload = {
        "api_key": API_KEY,
        "pin_id": pin_id,
        "pin": pin,
    }

    headers = {
        "Content-Type": "application/json",
    }

    try:
        logging.info(f"Verifying pin_id: {pin_id}")
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        
        response.raise_for_status()

        data = response.json()

        if response.status_code == 200 and "pinId" in data:
            return {"success": True, "message": "OTP verified successfully", "data": data}

        return {"success": False, "error": data.get("message", "Failed to verify OTP")}
    
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
