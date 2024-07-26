# SignLLM Demo Backend

This folder contains the python backend server (built on FastAPI) which launches all the machine learning models (e.g. MAE, DINO, LLaVA) used in the ASL translation pipeline.


## After cloning

To run the server you should have at least Python 3.10 available. If you use Windows, you can use [Git Bash](https://gitforwindows.org) (included with [GitHub desktop](https://github.com/apps/desktop)) to execute all the commands in this readme.

In a server setup, the python command can be obtained from an anaconda environment. It is only needed for the initial setup to create the virtual environment. Then all the commands use the virtual environment.

First, create the virtual environment where everything will be installed:

```bash
python3 -m venv .venv
```

Then, install all the pip packages and the machine-learning models:

```bash
make install-requirements
make install-all-models
```

Then you need to set up environment variables file. Copy the `.env.example` to create a file `.env` and fill out the values. See the section below on which to fill out when and how.

You can verify that all models can be executed by running this command, which also causes models downloaded from huggingface to actually get downloaded.

```bash
make test-all-models
```

Now you can start the development uvicorn FastApi server on port `1817`:

```bash
make start

# or for production to accept traffic from all IP addresses and disable
# filesystem watching and automatic reloading:
make start-production
```


## Environment variables (the `.env` file)

- `HUGGINGFACE_TOKEN` Your huggingface token, may be required to download private models (e.g. sign2vec before it gets published), otherwise it can be removed.
