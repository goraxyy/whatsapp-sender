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

## Setup (one-time)

### 1. Clone the repo

```bash
git clone https://github.com/goraxyy/whatsapp-sender.git
cd whatsapp-sender
```

### 2. Install dependencies

```bash
pip3 install pywhatkit
```

> **Note:** use `pip3`, not `pip` — macOS does not have a `pip` binary by default.

### 3. Fix the `python` command on macOS (one-time)

macOS ships with `python3` only, not `python`. Add a permanent alias:

```bash
echo "alias python=python3" >> ~/.zshrc && source ~/.zshrc
```

---

## Usage

### Quick test — dry-run on sample data

```bash
python3 sender.py contacts_sample.csv
```

Outputs a timestamped log to `logs/run_YYYYMMDD_HHMMSS.log`. Nothing is sent.

---

### Full flow — generate from parking scraper → dry-run

The scraper writes output only to Google Sheets, not a local file. Use this script to also save a local CSV:

```bash
cd ~/almaty-parking-scraper && python3 - << 'EOF'
import csv
from config import cfg
from dgis_client import DGisClient
from transformer import transform
from deduplicator import deduplicate

client = DGisClient()
raw = client.collect_all()
records = deduplicate([transform(i) for i in raw])
records = [r for r in records if r.get("название") != "н/д" or r.get("адрес") != "н/д"]
with open("parking_data.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=records[0].keys())
    w.writeheader()
    w.writerows(records)
print(f"Saved {len(records)} rows to parking_data.csv")
EOF
```

Then convert and run:

```bash
cp ~/almaty-parking-scraper/parking_data.csv ~/whatsapp-sender/
cd ~/whatsapp-sender
python3 generate_contacts.py parking_data.csv --out contacts.csv
python3 sender.py contacts.csv --mode dry-run
```

---

### Live mode (≤2 messages to your own number)

First create a file with your real number in the first rows:

```bash
head -1 contacts.csv > contacts_live.csv
sed -n '2,3p' contacts.csv | sed 's/+77000000000/+YOUR_REAL_NUMBER/g' >> contacts_live.csv
```

Then send:

```bash
python3 sender.py contacts_live.csv --mode live
```

WhatsApp Web opens in your browser (~2 min delay). **You must be logged in to WhatsApp Web.**

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
