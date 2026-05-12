# Selenium Data-Driven Testing — Send Message (Moodle Demo)

## Overview

This project automates the **Send Message** feature of the Mount Orange Moodle Demo site (`https://school.moodledemo.net/`) using Python `unittest` and Selenium WebDriver. It re-tests the functional cases from Project #2 with a data-driven approach plus two non-functional tests.

## Project Structure

```
.
├── SendMessageV2/                       # Original Katalon-exported test cases (per-TC scripts)
│   ├── TC002001.py — TC002011.py        # (TC002009, TC002010 are use-case tests, excluded)
│   └── Login.py
│
├── Level1/                              # Test data in CSV; locators hardcoded
│   ├── send_message_test.py
│   └── send_message_data.csv
│
├── Level2/                              # Test data AND locators in CSV
│   ├── send_message_test.py
│   └── send_message_data.csv
│
├── NonFunctional/
│   ├── nonfunctional_performance_test.py
│   └── nonfunctional_load_test.py
│
├── requirements.txt
└── README.md
```

## Test Coverage

**Functional Tests (TC-002-001 to TC-002-011):**
- TC-002-001 — empty message boundary (send disabled, textarea stays empty)
- TC-002-002 — single character `a`
- TC-002-003 — short text `hi`
- TC-002-004 — exact 4096-character maximum (upper boundary, valid)
- TC-002-005 — 4097 characters (over limit, textarea truncates to 4096)
- TC-002-006 — punctuation phrase
- TC-002-007 — special characters `@#$%^&*() — 123`
- TC-002-008 — emoji `Hi there! 😊🎉`
- TC-002-011 — large string (10000 chars, capped at 4096 by `maxlength`)
- TC-002-009, TC-002-010 are use-case tests and are excluded from this scope.

**Non-Functional Tests:**
- **Performance** — measures elapsed time from `Send` click to the bubble appearing; reports avg / p95 over 10 iterations
- **Load** — sends 50 messages back-to-back and asserts every one is present in the conversation

## Level 1 vs Level 2 Comparison

| Aspect | Level 1 | Level 2 |
|--------|---------|---------|
| Test data (recipient, message, expected) in CSV | ✅ | ✅ |
| Element selectors in CSV | ❌ | ✅ |
| Base URL in CSV | ❌ | ✅ |
| Reusability | Single site | Any matching site |

## Installation & Usage

**Requirements:**
```
selenium==3.141.0
urllib3==1.26.7
webdriver-manager
```

**Install:**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
pip install webdriver-manager
```

**Run Level 1:**
```powershell
python Level1\send_message_test.py
```

**Run Level 2:**
```powershell
python Level2\send_message_test.py
```

**Run a non-functional test:**
```powershell
python NonFunctional\nonfunctional_performance_test.py
python NonFunctional\nonfunctional_load_test.py
```

**Run a single original TC (for reference):**
```powershell
python SendMessageV2\TC002002.py
```

## Important Notes

- The demo site **resets every hour**; long runs that straddle the top of the hour will lose their session.
- The Send Message textarea enforces `maxlength="4096"`; messages above that are truncated at the input layer (the basis for boundary cases TC-002-005 and TC-002-011).
- Verification reads the last "send"-class message bubble via `(//div[@data-region='message' and contains(@class,' send ')])[last()]//p`.
- Emoji characters are typed via JavaScript (`element.value = ...; dispatchEvent('input')`) because ChromeDriver's `send_keys` cannot transmit characters outside the Basic Multilingual Plane.
- A 5-second wait is used before each verify to give Moodle's async send a chance to render the new bubble.
- All scripts log in as the `student` demo account (password `moodle26`).
- In Level 2, commas inside xpath expressions are encoded as `$$` in the CSV and substituted back to `,` when the data is loaded (CSV alone cannot quote them safely with the rest of the row).
