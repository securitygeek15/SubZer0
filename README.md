# SubZero

SubZero is a threaded, terminal-based subdomain reconnaissance tool built in Python.
It provides a live TUI dashboard, HTTP status filtering, safe interruption handling, and automatic result exporting.

## Features

- Threaded DNS resolution with concurrent subdomain scanning
- HTTP/HTTPS status code detection (auto-fallback between protocols)
- Live terminal UI (Rich-based) with real-time stats and progress
- Resolved IP address display for each subdomain
- Wildcard DNS detection to identify false positives
- Status code filtering (e.g., 200,403)
- CLI argument support for non-interactive usage
- Automatic result saving (TXT, optional JSON/CSV)
- Graceful Ctrl+C shutdown
- Modular architecture

## Project Structure

```
subzero/
├── main.py              # Entry point / CLI orchestration
├── scanner.py           # Threaded scanner engine
├── resolver.py          # DNS resolver + wildcard detection
├── http_checker.py      # HTTP/HTTPS status checker
├── banner.py            # Rich ASCII banner
├── requirements.txt     # Python dependencies
└── wordlists/
    └── common.txt       # 345 common subdomain prefixes
```

## Installation

Clone the repository:

```
git clone https://github.com/securitygeek15/SubZer0.git
cd subzero
```

Install dependencies:

```
pip install -r requirements.txt
```

## Usage

### Interactive mode

```
python main.py
```

### CLI mode

```
python main.py -d example.com
python main.py -d example.com -w wordlists/big.txt -t 50 -f 200,403
python main.py -d example.com --https --json --csv
python main.py -d example.com -o results/scan1 --json
```

### Arguments

| Argument | Description |
|---|---|
| `-d, --domain` | Target domain to scan |
| `-w, --wordlist` | Path to subdomain wordlist (default: wordlists/common.txt) |
| `-t, --threads` | Number of concurrent threads (default: 30) |
| `-f, --filter` | Comma-separated status codes to display (e.g. 200,403) |
| `--https` | Prefer HTTPS over HTTP for status checking |
| `--json` | Export results in JSON format |
| `--csv` | Export results in CSV format |
| `-o, --output` | Output file basename (without extension) |

### Status Code Filtering

Display only 200 responses:

```
200
```

Display 200 and 403 responses:

```
200,403
```

Press Enter to display all responses.

## Output

Results are automatically saved to `<domain>_subdomains.txt` with IP addresses and status codes.
Use `--json` or `--csv` for additional export formats.

## Notes

- Large wordlists may impact performance.
- Some domains use wildcard DNS, which may produce false positives — SubZero detects and warns about this.
- Use `--https` when scanning domains that enforce HTTPS.

## License

MIT License
