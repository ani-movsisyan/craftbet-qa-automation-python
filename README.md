# CraftBet QA Automation (Python)

## Requirements

- Python 3.10+
- Google Chrome
- Postman

## Install

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Create file `.env` in the project folder (it is in `.gitignore`):

```
CRAFTBET_USERNAME=<test account login>
CRAFTBET_PASSWORD=<test account password>
HEADLESS=false
```

## Run UI tests

```bash
pytest                                  # all tests
pytest tests/test_03_games.py           # one file
```

Results:

- `reports/report.html` – HTML report with screenshots
- `reports/screenshots/` – screenshots
- `reports/test_run.log` – log

## Postman

Files:

- `postman/CraftBet_API.postman_collection.json`
- `postman/CraftBet.postman_environment.json`

Get token:

1. Log in on https://craftbet.com.
2. Open DevTools (F12) → **Network**, filter by `ApiRequest`.
3. Open any request `ApiRequest` → **Payload** → copy the value of `Token`.

Paste the value to the `token` environment variable (Current value) and run the collection.
Run requests in order: 01 saves `clientId`, `currencyId` and the new session token for the next requests.

## Documentation

- Test scenarios and challenges: [docs/test_cases.md](docs/test_cases.md)
- Execution results: [docs/results](docs/results)
