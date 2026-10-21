import requests
from urllib.parse import urlparse

def check_ssl_certificate(url: str):

    parsed = urlparse(url)

    if parsed.scheme != "https":
        return {
            "has_ssl": False,
            "reason": "Not using HTTPS"
        }

    try:
        response = requests.get(url, timeout=5)
        return {
            "has_ssl": True,
            "status_code": response.status_code
        }
    except requests.exceptions.SSLError:
        return {
            "has_ssl": False,
            "reason": "Invalid SSL certificate"
        }
    except Exception as e:
        return {
            "has_ssl": False,
            "reason": str(e)
        }