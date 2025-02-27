from django.conf import settings
import requests
import logging

logger = logging.getLogger(__name__)


DOJAH_BASE_URL = "https://api.dojah.io/"


def verify_nin(nin):
    """
    Calls the Dojah API to verify NIN and fetch user details.
    """
    url = f"{DOJAH_BASE_URL}/api/v1/kyc/nin"
    headers = {
        "AppId": settings.DOJAH_APP_ID,
        "Authorization": settings.DOJAH_AUTHORIZATION,
    }
    params = {"nin": nin}

    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        if response.status_code == 200:
            return response.json()
        
        else:
            return {
                "error": f"HTTP error from Dojah: {response.status_code} {response.reason}",
                "details": response.json()
            }

        # if "entity" not in data or not data["entity"]:
        #     logger.error(f"NIN not found: {nin}")
        #     return {"error": "NIN not found in Dojah records"}

        # return data

    except requests.exceptions.Timeout:
        logger.error("Dojah API request timed out")
        return {"error": "Dojah API request timed out"}

    except requests.exceptions.ConnectionError:
        logger.error("Failed to connect to Dojah API")
        return {"error": "Failed to connect to Dojah API"}

    except requests.exceptions.HTTPError as err:
        logger.error(f"HTTP error from Dojah: {err}")
        return {"error": f"HTTP error from Dojah: {err}"}

    except requests.exceptions.RequestException as err:
        logger.error(f"Unexpected error: {err}")
        return {"error": "An unexpected error occurred while verifying NIN"}
