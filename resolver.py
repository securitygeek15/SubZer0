import socket

def resolve_domain(domain: str) -> bool:
    try:
        socket.gethostbyname(domain)
        return True
    except socket.gaierror:
        return False