# SignLLaVA Demo Backend

This folder contains the python backend server (built on FastAPI) which launches all the machine learning models (e.g. MAE, DINO, LLaVA) used in the ASL translation pipeline.


## After cloning

> **Note:** This a short list of commands. For a full-on tutorial see the [Installing on Rockfish and your laptop](../docs/installing-on-rockfish-and-your-laptop.md) file.

> **Requirement:** To run the server you must have at least Python 3.10 available. Also, if you use Windows, you can use [Git Bash](https://gitforwindows.org) (included with [GitHub desktop](https://github.com/apps/desktop)) to execute all the commands in this README.

> **Tip:** In a server setup, the python command can be obtained from an anaconda environment. It is only needed for the initial setup to create the virtual environment. Then all the commands use the virtual environment.

First, create the virtual environment where everything will be installed:

```bash
python3 -m venv .venv
```

Then, install all the pip packages and the machine-learning models:

```bash
make install-requirements
make install-all-models
```

Then you need to set up environment variables file. Copy the `.env.example` to create a file `.env` and fill out the values. See the [section below](#environment-variables-the-env-file) on which to fill out when and how.

```bash
# setup the .env
cp .env.example .env
chmod 600 .env # important for a cluster setup with other users

# fill out your huggingface token
nano .env
```

You can verify that all models can be executed by running this command, which also causes models downloaded from huggingface to actually get downloaded.

```bash
make test-all-models
```

> **Note:** Huggingface models are downloaded into `~/.cache/huggingface`. If you don't have the necessary disk quota in your home folder, you can turn this folder into a symlink to a place where you do have the quota. This is important for the LLaMa model which has several gigabytes. You can do the same for the `backend/checkpoints` folder.

Now you can start the development uvicorn FastApi server on port `1817`:

```bash
make start

# or for production to accept traffic from all IP addresses and disable
# filesystem watching and automatic reloading:
make start-production
```


## Environment variables (the `.env` file)

- `HF_TOKEN` Your huggingface token, may be required to download private models (e.g. sign2vec before it gets published), otherwise it can be removed.
