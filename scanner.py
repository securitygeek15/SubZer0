from concurrent.futures import ThreadPoolExecutor, as_completed
from resolver import resolve_domain
from http_checker import check_http
import threading


stop_event = threading.Event()


def process_subdomain(domain: str, word: str):
    if stop_event.is_set():
        return None

    word = word.strip()
    if not word:
        return None

    subdomain = f"{word}.{domain}"

    if resolve_domain(subdomain):
        status = check_http(subdomain)
        return (subdomain, status)

    return None


def scan(domain: str, wordlist_path: str, threads: int = 30):
    with ThreadPoolExecutor(max_workers=threads) as executor:
        futures = []

        with open(wordlist_path, "r") as file:
            for word in file:
                if stop_event.is_set():
                    break

                futures.append(
                    executor.submit(process_subdomain, domain, word)
                )

        try:
            for future in as_completed(futures):
                if stop_event.is_set():
                    break

                result = future.result()
                if result:
                    yield result

        except KeyboardInterrupt:
            stop_event.set()
            executor.shutdown(wait=False, cancel_futures=True)
            raise