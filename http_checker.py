import requests 

def check_http(domain : str) -> int | None:
    try:
        response = requests.get(f"http://{domain}",timeout=3,allow_redirects=True)
        return response.status_code
    except requests.RequestException:
        return None 
    
    