# SubZero

SubZero is a threaded, terminal-based subdomain reconnaissance tool built in Python.  
It provides a live TUI dashboard, HTTP status filtering, safe interruption handling, and automatic result exporting.

## Features

- Threaded DNS resolution
- HTTP status code detection
- Live terminal UI (Rich-based)
- Status code filtering (e.g., 200,403)
- Automatic result saving
- Graceful Ctrl+C shutdown
- Modular architecture

## Project Structure

subzero/
│
├── main.py
├── scanner.py
├── resolver.py
├── http_checker.py
├── banner.py
└── wordlists/
    └── common.txt

## Installation

Clone the repository:

git clone https://github.com/securitygeek15/subzero.git  
cd subzero  

Install dependencies:

pip install -r requirements.txt

## Usage

Run:

python main.py  

You will be prompted to enter:

- Target domain
- Status codes to display (optional)

Results are automatically saved to:

<domain>_subdomains.txt

## Status Code Filtering

Display only 200 responses:

200

Display 200 and 403 responses:

200,403

Press Enter to display all responses.

## Notes

- Large wordlists may impact performance.
- For development, use smaller wordlists (500–1000 entries).
- Some domains use wildcard DNS, which may produce false positives.

## Roadmap

- Wildcard DNS detection
- Async scanning engine
- HTTPS fallback support
- JSON export
- CLI argument support
- Packaging as a pip-installable tool

## License

MIT License