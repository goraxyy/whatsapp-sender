# DECISIONS.md — WhatsApp Sender

**Time taken:** ~3 hours total (design, implementation, docs, debugging dependency issues)

---

## 1. Library choice — `pywhatkit` vs alternatives

| Option | Pros | Cons | Decision |
|--------|------|------|----------|
| **pywhatkit** | Zero setup, free, no API key, pure Python | Requires logged-in browser session; needs Flask/Pillow/pyautogui at runtime | ✅ **Chosen** |
| WhatsApp Business API (Meta Cloud) | Official, scalable, reliable | Business account required, paid for volume, complex OAuth | ❌ Overkill for demo |
| Raw Selenium + WA Web | Full control | Brittle CSS selectors, high maintenance, same browser requirement | ❌ More complexity, same limitations |
| Twilio WhatsApp API | Clean REST API | Paid, sandbox phone restrictions, requires approval | ❌ Cost barrier |

**Verdict:** `pywhatkit` is the right tool for a demo/principle project. It wraps WhatsApp Web automation and sends without any API keys.

**Lesson learned:** installing with `--no-deps` to save time caused a `pywhatkit not installed` error at runtime in live mode, because pywhatkit's own imports (Flask, Pillow, pyautogui) were missing. The fix was to run `pip3 install pywhatkit` without `--no-deps` for live mode.

---

## 2. Two-mode architecture (dry-run / live)

**Decision:** `dry-run` is the default mode; `live` requires an explicit `--mode live` flag.

**Rationale:**
- Prevents accidental sends during development or grading.
- The task explicitly required this split.
- The dry-run produces a structured log file, making it easy to inspect what *would* have been sent across the full parking dataset (354 rows) without ever touching real numbers.

**Alternative considered:** environment variable (`SEND_MODE=live`) — rejected in favour of a CLI flag because it's more explicit and discoverable via `--help`.

---

## 3. Input format — CSV with `phone` + `message` columns

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

**Lesson learned:** the placeholder phone `+77000000000` passes format validation (correct digit count) but does not exist on WhatsApp. pywhatkit opened the chat but WhatsApp showed "number does not exist". The fix was to replace the placeholder with a real number before running live mode.

**Trade-off:** format-only validation is sufficient for a demonstration. Real existence checks would require a WhatsApp API call.

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

---

## 7. Dependency issues encountered during setup

Setting up the project on macOS (Python 3.9, system install) required several extra steps not anticipated in the initial requirements. All issues were resolved and the correct install command is now documented in README.

| Problem | Cause | Fix |
|---------|-------|-----|
| `zsh: command not found: pip` | macOS has no `pip` binary | Use `pip3` instead |
| `zsh: command not found: python` | macOS has no `python` binary | Use `python3`, or add `alias python=python3` to `~/.zshrc` |
| `pip3 install -r requirements.txt` hung | Slow dependency resolver with many packages | Use `pip3 install pywhatkit --no-deps` for dry-run, full `pip3 install pywhatkit` for live |
| `ModuleNotFoundError: No module named 'dotenv'` | Scraper dependencies not installed | `pip3 install python-dotenv requests` |
| `ImportError: numpy._core.multiarray failed to import` | Outdated/missing numpy with shapely | `pip3 install numpy shapely` |
| `ModuleNotFoundError: No module named 'cryptography'` | Missing Google auth dependency | `pip3 install cryptography` |
| `ModuleNotFoundError: No module named 'requests_oauthlib'` | Missing OAuth dependency | `pip3 install requests-oauthlib google-auth-oauthlib google-api-python-client` |
| `pywhatkit not installed` error at runtime in live mode | Installed with `--no-deps`, missing Flask/Pillow/pyautogui | `pip3 install pywhatkit` (with deps) |
| Scraper produces no local `parking_data.csv` | Scraper only writes to Google Sheets | Added inline script to also save local CSV |
| First live send went to placeholder `+77000000000` | `generate_contacts.py` uses a placeholder phone | Replace placeholder with real number before live mode |
