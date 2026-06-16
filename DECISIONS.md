# DECISIONS.md — WhatsApp Sender

**Time taken:** ~2 hours (design, implementation, docs)

---

## 1. Library choice — `pywhatkit` vs WhatsApp Business API vs Selenium

| Option | Pros | Cons | Decision |
|--------|------|------|----------|
| **pywhatkit** | Zero setup, free, no API key, pure Python | Requires logged-in browser session; not 100% headless | ✅ **Chosen** |
| WhatsApp Business API (Meta Cloud) | Official, scalable, reliable | Business account required, paid for volume, complex OAuth | ❌ Overkill for demo |
| Raw Selenium + WA Web | Full control | Brittle CSS selectors, high maintenance, same browser req. | ❌ More complexity, same limitations |
| Twilio WhatsApp API | Clean REST API | Paid, sandbox phone restrictions, requires approval | ❌ Cost barrier |

**Verdict:** `pywhatkit` is the right tool for a demo/principle project. It wraps WhatsApp Web automation and sends without any API keys.

---

## 2. Two-mode architecture (dry-run / live)

**Decision:** `dry-run` is the default mode; `live` requires an explicit `--mode live` flag.

**Rationale:**
- Prevents accidental sends during development or grading.
- The task explicitly required this split.
- The dry-run produces a structured log file, making it easy to inspect what *would* have been sent across the full parking dataset without ever touching real numbers.

**Alternative considered:** environment variable (`SEND_MODE=live`) — rejected in favour of a CLI flag because it's more explicit and discoverable via `--help`.

---

## 3. Input format — CSV/TSV with `phone` + `message` columns

**Decision:** two-column flat CSV is the contract.

**Rationale:**
- Simplest schema that satisfies the task (table in → messages out).
- Works directly with Excel/Google Sheets exports.
- `generate_contacts.py` bridges the gap from the parking scraper's multi-column output.

**Alternative:** accept JSON or a Google Sheet URL directly — more flexible but adds dependencies and complexity with no benefit for a demo.

---

## 4. Phone validation strategy

**Decision:** regex `^\+?[1-9]\d{6,14}$` + normalise to E.164 (`+XXXXXXXXXXX`).

**Rationale:**
- Catches obvious invalid inputs (`+invalid-num`, empty, letters).
- Strips formatting characters (spaces, dashes, brackets) before validation.
- Lenient enough to accept KZ (`+7 777 123 45 67`), international numbers, etc.

**Trade-off:** does not validate that the number actually exists on WhatsApp. That would require an API call. Format validation is sufficient for a demonstration; live errors from pywhatkit are caught and logged per-row.

---

## 5. Error handling philosophy — never crash, always log

**Decision:** every row-level error is caught, logged with context, and the program continues. Only fatal startup errors (file not found, bad CSV schema) exit early.

**Rationale:**
- A bulk sender that stops on the first bad row is useless in production.
- The log file gives a full audit trail: which rows succeeded, which were skipped, and why.
- The task explicitly required robust error handling.

---

## 6. Live-mode hard cap (2 messages)

**Decision:** `MAX_LIVE_MESSAGES = 2` constant, enforced before each send attempt.

**Rationale:**
- Direct compliance with the task constraint against mass-sending.
- Named constant makes it obvious, auditable, and easy to find in code review.
- Rows after the cap are logged at INFO level (not silently dropped).
