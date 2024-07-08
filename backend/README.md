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


## Installing Sign Llava

Upgrade PIP just like the LLava repo recommends, just in case:

```bash
.venv/bin/pip3 install --upgrade pip  # enable PEP 660 support
```

Clone the sign llava into the `models` directory.

```bash
cd models
git clone git@github.com:JSALT2024/Sign_LLaVA.git
cd Sign_LLaVA
git checkout phoenix
git pull
cd ../..
```

Install the model into the virtual environment without dependencies (the dependencies have been already included in the `requirements.txt` file of this backend project).

```bash
.venv/bin/pip3 install --no-deps --editable ./models/Sign_LLaVA
```

You can then test that plain Llava works by running:

```bash
.venv/bin/python3 -m app.debug.test_plain_llava
```

And you can test the sign llava by running:

```bash
.venv/bin/python3 -m app.debug.test_sign_llava
```
