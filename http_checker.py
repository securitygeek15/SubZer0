import requests


def check_http(domain: str, prefer_https: bool = True) -> int | None:
    schemes = ["https", "http"] if prefer_https else ["http"]
    for scheme in schemes:
        try:
            response = requests.get(
                f"{scheme}://{domain}", timeout=3, allow_redirects=True
            )
            return response.status_code
        except requests.RequestException:
            continue
    return None
