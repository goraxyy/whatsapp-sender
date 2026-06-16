# WhatsApp Sender — Demonstration of Principle

Reads a CSV table of phone numbers + messages and either logs them (dry-run) or sends them via WhatsApp Web (live).

> **Hard limit:** bulk sending to third-party numbers is forbidden.  
> Live mode is capped at **2 messages** and is only for sending to your own / test number.

---

## How it works

```
contacts.csv  →  sender.py  →  logs/run_*.log   (dry-run)
                            →  WhatsApp Web      (live, ≤2 msgs)
```

For use with the [Almaty Parking Scraper](https://github.com/goraxyy/almaty-parking-scraper), run `generate_contacts.py` first to convert the parking CSV into the required format.

---

## Installation

```bash
git clone https://github.com/goraxyy/whatsapp-sender.git
cd whatsapp-sender
pip install -r requirements.txt
```

**Dependency:** `pywhatkit` — opens WhatsApp Web via browser automation. No API keys needed.

---

## Input format

CSV or TSV file with two required columns:

| phone | message |
|-------|---------|
| +77771234567 | Hello from parking data! |
| +77779999999 | Another message |

- **phone:** E.164 format (`+` + country code + number, 7–15 digits). Spaces/dashes stripped automatically.
- **message:** plain text. Multi-line supported.
- Invalid numbers and empty messages are **skipped with a warning** — the program never crashes on bad data.

---

## Commands

### Dry-run (default — safe, nothing is sent)

```bash
python sender.py contacts_sample.csv
# or explicitly:
python sender.py contacts_sample.csv --mode dry-run
```

Outputs a timestamped log to `logs/run_YYYYMMDD_HHMMSS.log`.

### Live mode (sends ≤2 messages to your own number)

```bash
python sender.py my_contacts.csv --mode live
```

WhatsApp Web opens in your browser (~2 min delay). **You must be logged in to WhatsApp Web.**

### Convert parking scraper output → contacts

```bash
# After running almaty-parking-scraper to get parking_data.csv:
python generate_contacts.py parking_data.csv --out contacts.csv
python sender.py contacts.csv --mode dry-run
```

---

## Error handling

| Situation | Behaviour |
|-----------|-----------|
| File not found | Logs error, exits with code 1 |
| Missing columns | Logs error, exits with code 1 |
| Invalid phone number | Logs warning, skips row, continues |
| Empty message | Logs warning, skips row, continues |
| pywhatkit / network error | Logs error per row, continues to next |
| Live cap reached (2 msgs) | Logs info, stops sending, exits cleanly |

---

## Project structure

```
whatsapp-sender/
├── sender.py              # Main entry point
├── generate_contacts.py   # Convert parking CSV → contacts.csv
├── contacts_sample.csv    # Sample input (includes intentionally invalid rows)
├── requirements.txt
├── DECISIONS.md
└── logs/                  # Created on first run (gitignored)
```
