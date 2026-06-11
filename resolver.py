import socket
import uuid


def resolve_domain(domain: str) -> str | None:
    try:
        return socket.gethostbyname(domain)
    except socket.gaierror:
        return None
    except OSError:
        return None


def check_wildcard_dns(domain: str) -> str | None:
    random_sub = f"{uuid.uuid4()}.{domain}"
    return resolve_domain(random_sub)
