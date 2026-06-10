# Tests

Run tests with pytest from the repository root. Some tests are unit-level and do not require a running database. Integration tests require a test database and environment variables (e.g., DATABASE_URL_TEST).

Examples:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r backend/requirements.txt
pip install pytest
pytest -q
```

For DB-enabled tests, set `DATABASE_URL_TEST` to a Postgres test instance and run migrations before executing tests.
