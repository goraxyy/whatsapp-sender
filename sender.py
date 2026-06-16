#!/usr/bin/env python3
"""
WhatsApp Bulk Sender — demonstration of principle.
Modes:
  --mode dry-run  (default): log messages to file instead of sending
  --mode live     : send 1-2 messages via pywhatkit to your own number
"""

import argparse
import csv
import logging
import os
import re
import sys
import time
from datetime import datetime
from pathlib import Path

# ---------------------------------------------------------------------------
# Logging setup
# ---------------------------------------------------------------------------
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)
LOG_FILE = LOG_DIR / f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)
log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
PHONE_RE = re.compile(r"^\+?[1-9]\d{6,14}$")   # E.164-ish, 7-15 digits
MAX_LIVE_MESSAGES = 2                             # hard cap for live mode

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def validate_phone(raw: str) -> tuple[bool, str]:
    """Normalise and validate a phone number string.

    Returns (is_valid, normalised_number_or_error_reason).
    """
    cleaned = re.sub(r"[\s\-\(\)\.]+", "", raw.strip())
    if not cleaned:
        return False, "empty number"
    if not PHONE_RE.match(cleaned):
        return False, f"invalid format: '{raw}'"
    # Ensure leading +
    if not cleaned.startswith("+"):
        cleaned = "+" + cleaned
    return True, cleaned


def load_input(path: str) -> list[dict]:
    """Load CSV/TSV input. Expects columns: phone, message (+ any extras ignored)."""
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Input file not found: {path}")
    delimiter = "\t" if p.suffix.lower() == ".tsv" else ","
    rows = []
    with p.open(encoding="utf-8-sig") as f:
        reader = csv.DictReader(f, delimiter=delimiter)
        required = {"phone", "message"}
        if reader.fieldnames is None or not required.issubset(
            {c.strip().lower() for c in reader.fieldnames}
        ):
            raise ValueError(
                f"CSV must have 'phone' and 'message' columns. "
                f"Found: {reader.fieldnames}"
            )
        # Normalise column names to lowercase
        for row in reader:
            rows.append({k.strip().lower(): v for k, v in row.items()})
    return rows


# ---------------------------------------------------------------------------
# Core send logic
# ---------------------------------------------------------------------------

def dry_run(rows: list[dict]) -> None:
    """Write would-be messages to log only — nothing is sent."""
    log.info("=== DRY-RUN MODE — no messages will be sent ===")
    ok = err = 0
    for i, row in enumerate(rows, 1):
        phone_raw = row.get("phone", "")
        message = row.get("message", "").strip()

        valid, phone_or_err = validate_phone(phone_raw)
        if not valid:
            log.warning("Row %-4d  SKIP   %s", i, phone_or_err)
            err += 1
            continue
        if not message:
            log.warning("Row %-4d  SKIP   empty message for %s", i, phone_or_err)
            err += 1
            continue

        log.info(
            "Row %-4d  DRY    to=%s  msg_len=%d  preview=%.60s",
            i, phone_or_err, len(message), message.replace("\n", " "),
        )
        ok += 1

    log.info("--- Summary: %d would-be sends, %d skipped/invalid ---", ok, err)
    print(f"\n\u2713 Dry-run complete. Log saved to: {LOG_FILE}")


def live_send(rows: list[dict]) -> None:
    """Send up to MAX_LIVE_MESSAGES messages via pywhatkit (opens WhatsApp Web)."""
    try:
        import pywhatkit as pwk
    except ImportError:
        log.error(
            "pywhatkit not installed. Run:  pip install pywhatkit"
        )
        sys.exit(1)

    log.info(
        "=== LIVE MODE — will send up to %d message(s) ===", MAX_LIVE_MESSAGES
    )
    sent = err = 0

    for i, row in enumerate(rows, 1):
        if sent >= MAX_LIVE_MESSAGES:
            log.info("Reached live-send cap (%d). Remaining rows skipped.", MAX_LIVE_MESSAGES)
            break

        phone_raw = row.get("phone", "")
        message = row.get("message", "").strip()

        valid, phone_or_err = validate_phone(phone_raw)
        if not valid:
            log.warning("Row %-4d  SKIP   %s", i, phone_or_err)
            err += 1
            continue
        if not message:
            log.warning("Row %-4d  SKIP   empty message for %s", i, phone_or_err)
            err += 1
            continue

        # Schedule 2 minutes from now
        now = datetime.now()
        send_hour = now.hour
        send_min = now.minute + 2
        if send_min >= 60:
            send_min -= 60
            send_hour = (send_hour + 1) % 24

        try:
            log.info(
                "Row %-4d  SEND   to=%s  scheduled=%02d:%02d",
                i, phone_or_err, send_hour, send_min,
            )
            pwk.sendwhatmsg(
                phone_or_err,
                message,
                send_hour,
                send_min,
                wait_time=15,
                tab_close=True,
                close_time=3,
            )
            sent += 1
            log.info("Row %-4d  OK     message queued for %s", i, phone_or_err)
            time.sleep(5)
        except Exception as exc:  # noqa: BLE001
            log.error("Row %-4d  ERROR  %s — %s", i, phone_or_err, exc)
            err += 1

    log.info("--- Summary: %d sent, %d errors ---", sent, err)
    print(f"\n\u2713 Live-send complete. Log saved to: {LOG_FILE}")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="WhatsApp Sender (demonstration). Default mode is dry-run."
    )
    parser.add_argument(
        "input",
        nargs="?",
        default="contacts.csv",
        help="Path to CSV/TSV with columns: phone, message  (default: contacts.csv)",
    )
    parser.add_argument(
        "--mode",
        choices=["dry-run", "live"],
        default="dry-run",
        help="dry-run (default): log only. live: actually send (max 2 msgs).",
    )
    args = parser.parse_args()

    log.info("Starting WhatsApp sender | mode=%s | input=%s", args.mode, args.input)

    try:
        rows = load_input(args.input)
        log.info("Loaded %d row(s) from %s", len(rows), args.input)
    except (FileNotFoundError, ValueError) as exc:
        log.error("Input error: %s", exc)
        sys.exit(1)

    if args.mode == "live":
        live_send(rows)
    else:
        dry_run(rows)


if __name__ == "__main__":
    main()
