# SignLLM Demo Backend

## After cloning

Create virtual environment:

```bash
python3 -m venv .venv
```

Install packages into the environment:

```bash
.venv/bin/pip3 install -r requirements.txt
```

Start the service locally for development:

```bash
.venv/bin/python3 -m uvicorn app.api.main:app --port 1817 --reload
```

Start the service for production:

```bash
.venv/bin/python3 -m uvicorn app.api.main:app --host 0.0.0.0 --port 1817
```
