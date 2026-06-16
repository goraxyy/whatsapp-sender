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

### 2. Install dependency

```bash
pip3 install pywhatkit --no-deps
```

### 3. (Optional) Fix `python` command on macOS

macOS ships without a `python` binary — only `python3`. Add a permanent alias:

```bash
echo "alias python=python3" >> ~/.zshrc && source ~/.zshrc
```

After this, you can use `python` instead of `python3` in all commands below.

---

## Usage

### Quick test — dry-run on sample data

```bash
python3 sender.py contacts_sample.csv
```

Outputs a timestamped log to `logs/run_YYYYMMDD_HHMMSS.log`. Nothing is sent.

---

### Full flow — parking scraper → dry-run

> Run from the folder that contains `parking_data.csv`, or pass the full path.

```bash
# Step 1: find your parking CSV if unsure where it is
find ~ -name "parking_data.csv" 2>/dev/null

# Step 2: convert parking data → contacts.csv
python3 /path/to/whatsapp-sender/generate_contacts.py /path/to/parking_data.csv --out contacts.csv

# Step 3: dry-run over all contacts
python3 /path/to/whatsapp-sender/sender.py contacts.csv --mode dry-run
```

Or if you copy `parking_data.csv` into the project folder:

```bash
cp /path/to/parking_data.csv ~/whatsapp-sender/
cd ~/whatsapp-sender
python3 generate_contacts.py parking_data.csv --out contacts.csv
python3 sender.py contacts.csv --mode dry-run
```

---

### Live mode (sends ≤2 messages to your own number)

```bash
python3 sender.py contacts.csv --mode live
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
