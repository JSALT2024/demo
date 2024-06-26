# Development on Rockfish

> **Note:** All the used ssh commands will use `clsp-mayer` username because I'm going to be copy-pasting these most often. You need to replace these with your username.


## Connecting to a head machine

Use this command to connect:

```bash
ssh clsp-mayer@login.rockfish.jhu.edu
```

There are actually 3 head nodes (`login01`, `login02`, `login03`) and you will be connected to one of them randomly.


## Cloning repo to your home folder

> **Note:** To clone the private repo and/or to push changes you need to setup SSH keys. See [this github manual](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent) on how to create a key pair then upload the key to your github account.

I have created a `jsalt` folder in my home directory and then cloned the `demo` repository there:

```bash
git clone git@github.com:JSALT2024/demo.git
```


## Setting up the conda environment

> **Note:** We need to set up conda (instead of venv) because it lets us specify the python version.

After logging in to Rockfish, activate conda (ANAconda!):

```bash
module load anaconda
```

> **Important:** This MUST be done from the head node, because doing this on the worker node does not work. It sets the `$PATH` variable to something like `/data/apps/...centos.../..gcc../...anaconda.../bin`, where these cluster-wide apps are installed.

You can verify that the `conda` command works:

```bash
conda -V
```

Now, lets create a new conda environment:

```bash
conda create --name signllm-demo python=3.10
```

To list the existing environments use:

```bash
conda info --envs
```

Also, to remove the env, you can use:

```bash
conda remove --name signllm-demo --all
```


## Activate conda environment

You need to activate the conda environment to get access to the proper python version:

```bash
conda activate signllm-demo
```

Now if you ask, where is `python3`, it should be the one from the conda env:

```bash
which python3
```


## Creating python venv

With the active conda environment, you can create the venv:

```bash
cd ~/jsalt/demo/backend
python3 -m venv .venv
.venv/bin/pip3 install -r requirements.txt
```


## Starting an interactive worker job

This is how you can get an interactive worker job running with a GPU available:

```bash
srun -p mig_class --gpus 1 -u --pty bash -i
```

Within this job you can start the backend service:

```bash
# without reloading, for production:
.venv/bin/python3 -m uvicorn app.api.main:app --host 0.0.0.0 --port 1817
```


## Tunelling HTTP communication through SSH

This needs to be done in 2 steps:

1. You need to tunnel from your laptop to one of the rockfish head nodes.
2. You need to tunnel from the worker to that rockfish head node you've been assigned during the first step (since there are three head nodes, remember?).

First, from your laptop, start the tunnel to a rockfish head node:

```bash
ssh -L 1817:localhost:1817 clsp-mayer@login.rockfish.jhu.edu
```

Note down the head node number you were connected to, e.g. `login01`.

Now, inside the worker node, run the HTTP server in the background by appending `&` after the command.

> **Note:** You can later kill it by running `ps`, getting the process ID and running the `kill <process-id>` command.

In the worker node, start the second leg of the forward:

```bash
# replace login01 with the specific head node number the first tunnel openned to
ssh -NL 1817:localhost:1817 login01
```

**TODO:** Test it out, maybe we need to remap the ports, since there are some clashes still.
