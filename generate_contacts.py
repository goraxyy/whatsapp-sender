#!/usr/bin/env python3
"""
Generate contacts.csv from the parking scraper output.

Usage:
    python generate_contacts.py parking_data.csv [--out contacts.csv]

Reads the almaty-parking-scraper CSV (columns include 'название', 'адрес', etc.)
and produces a contacts.csv with columns: phone, message.

Because real parking spots don't have phone numbers in the scraper data,
this script uses a PLACEHOLDER phone (+77000000000) — demonstrating the
transformation logic while complying with the no-spam constraint.

Replace the placeholder with real numbers from another source.
"""

import argparse
import csv
import sys
from pathlib import Path

PLACEHOLDER_PHONE = "+77000000000"  # replace with real number column if available

MESSAGE_TEMPLATE = (
    "Здравствуйте! Информация о парковке:\n"
    "\U0001f4cd {name}\n"
    "\U0001f5fa {address}\n"
    "\U0001f4b0 {paid} | Тариф: {tariff}\n"
    "\U0001f550 {hours}\n"
    "\U0001f517 {url}"
)


def build_message(row: dict) -> str:
    return MESSAGE_TEMPLATE.format(
        name=row.get("название") or row.get("Название") or "н/д",
        address=row.get("адрес") or row.get("Адрес") or "н/д",
        paid=row.get("платная") or row.get("Платная?") or "н/д",
        tariff=row.get("тариф") or row.get("Тариф") or "н/д",
        hours=row.get("часы_работы") or row.get("Часы работы") or "н/д",
        url=row.get("ссылка_2гис") or row.get("Ссылка на 2ГИС") or "н/д",
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Convert parking CSV → contacts.csv")
    parser.add_argument("input", help="Path to parking_data.csv from almaty-parking-scraper")
    parser.add_argument("--out", default="contacts.csv", help="Output file (default: contacts.csv)")
    args = parser.parse_args()

    src = Path(args.input)
    if not src.exists():
        print(f"ERROR: file not found: {args.input}", file=sys.stderr)
        sys.exit(1)

    with src.open(encoding="utf-8-sig") as fin, \
         open(args.out, "w", newline="", encoding="utf-8") as fout:

        reader = csv.DictReader(fin)
        writer = csv.DictWriter(fout, fieldnames=["phone", "message"])
        writer.writeheader()

        count = 0
        for row in reader:
            writer.writerow({
                "phone": PLACEHOLDER_PHONE,
                "message": build_message(row),
            })
            count += 1

    print(f"\u2713 Wrote {count} rows to {args.out}")


if __name__ == "__main__":
    main()
