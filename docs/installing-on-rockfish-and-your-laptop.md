# Installing on Rockfish and your laptop

> **Note:** Rockfish is a compute cluster running at the Johns Hopkins University in Baltimore. Its documentation can be found at: https://www.arch.jhu.edu/guide/

> **Note:** This documentation is rockfish-specific, but the concepts should be applicable to any other compute cluster. So feel free to read on anyways.

> **Note:** All the used ssh commands will use my `clsp-mayer` username. You need to replace these with your username in all occurences.

We want to arrive to a final setup, where the backend will be running inside of an interactive job on a GPU machine (for example `gpu13`), the frontend will be running on your laptop, and the frontend will access the backend through a two-step SSH tunnel that we set up (your laptop `->` login node `->` the interactive job). This setup is captured in the following diagram:

<img src="img/rockfish-ssh-setup.svg" alt="Diagram of the Rockfish setup with the SSH tunnel" />

If you have the backend server already installed, jump right to the [Setting up the SSH tunnel](#setting-up-the-ssh-tunnel) section. Otherwise read from start to the end, or navigate to a specific section:

- [Installing the backend server](#installing-the-backend-server)
    - [Creating a Python 3.10 virtual environment](#creating-a-python-310-virtual-environment)
    - [Setting up filesystem symlinks (optional)](#setting-up-filesystem-symlinks-optional)
    - [Starting an interactive GPU job](#starting-an-interactive-gpu-job)
    - [Installing and testing ML models](#installing-and-testing-ml-models)
    - [Starting the backend server](#starting-the-backend-server)
- [Setting up the SSH tunnel](#setting-up-the-ssh-tunnel)
    - [Quality of life commands for the SHH tunnel](#quality-of-life-commands-for-the-shh-tunnel)
- [Setting up frontend](#setting-up-frontend)
- [Managing conda environments](#managing-conda-environments)


## Installing the backend server


### Creating a Python 3.10 virtual environment

For the backend we only need `Python 3.10`, which we can obtain from the `anaconda` module that's installed on Rockfish. We can do all of the following tasks from a login node, no need to start any interactive job.

Connect to Rockfish:

```bash
ssh clsp-mayer@login.rockfish.jhu.edu
```

> **Note:** Rockfish has three login nodes (`login01`, `login02`, `login03`) and we cannot choose which we connect to. We get one assigned automatically when we connect to `login.rockfish.jhu.edu`.

Pick a folder, say `~/jsalt/demo` and clone the source code:

```bash
git clone git@github.com:JSALT2024/demo.git ~/jsalt/demo
```

Now we need to set up the python virtual environment in the backend folder (i.e. we need to create the `~/jsalt/demo/.venv` folder). For that we will use the `anaconda` module that's installed on rockfish.

From within the login node, activate the `anaconda` module and create a conda environment for the demo with `Python 3.10` (not to use the environment via conda, but just to get a stable access to a `Python 3.10` interpreter). See the [Managing conda environments](#managing-conda-environments) section on how to do that.

> **Warning:** Do not use the `python3` command that is available by default. That command uses a different python installation for each machine, because it's the python that's intrinsic to that machine's operating system.

After you create the conda environment and activate it, you should see the following prompt:

```
(signllava-demo) [clsp-mayer@login01 ~]$
```

Now you can create the `.venv` folder in the cloned repository:

```bash
# enter the backend folder
cd ~/jsalt/demo/backend

# create the virtual environment in the `.venv` folder
python3 -m venv .venv
```

After this point, you no longer need to use conda. You can deactivate the environment by running `conda deactivate`. All the following commands will use the `python3` executable that has been created inside the `.venv` folder and therefore will use the conda environment's python without needing to activate anything.

If you ever need to use the backend's python with all of its packages yourself, just type in the full python executable path:

```bash
.venv/bin/python3
```

Or possibly activate the virtual environment:

```bash
source .venv/bin/activate
```


### Setting up filesystem symlinks (optional)

Before we actually download the model checkpoints for LLaMa and other models, you might want to create a symlink for the `backend/checkpoints` folder and the `~/.cache/huggingface` folder. This is because your home-folder quota might be relatively low and it's better to download these models to some other filesystem designed for large file storage.

I pointed the symlinks to the `scratch4` filesystem via the `scratch4` symlink I had in my home folder. You need to check and update these commands to use them for your setup (use your username in a few places):

```bash
# remove the real folders if they exist (especially the huggingface cache)
rm -rf ~/.cache/huggingface
rm -rf ~/jsalt/demo/backend/checkpoints

# create the target folders
mkdir -p ~/scratch4/clsp-mayer/huggingface_cache
mkdir -p ~/scratch4/clsp-mayer/demo_backend_checkpoints

# create the symlinks
ln -s ~/scratch4/clsp-mayer/huggingface_cache ~/.cache/huggingface
ln -s ~/scratch4/clsp-mayer/demo_backend_checkpoints ~/jsalt/demo/backend/checkpoints
```


### Starting an interactive GPU job

The following tasks will be more CPU intensive and very last ones will actually test the machine learning models so we need to have GPU access.

This command depends very much on your account rights on Rockfish, but this is the command I used to develop the system. It should work for you as well for at least 6 months after the workshop:

```bash
srun -N 1-1 -n 12 --gpus 1 -p a100 --time=3-00:00:00 --pty bash
```

It does the following:
- starts an interactive `bash` session (i.e. `srun --pty bash`)
- on a single machine `-N 1-1`
- with 12 CPU cores `-n 12`
- with one GPU card `--gpus 1`
- on the A100 partition `-p a100`
- with time limit increased to 3 days `--time=3-00:00:00`

After the job starts you should have a shell inside a GPU node, something like this:

```
[clsp-mayer@gpu13 ~]$
```

Continue with the rest of the tutorial inside this job.

> **Note:** If you're adapting this to your own cluster, see the [hardware requirements](hardware-requirements.md) file to see how many resources you need for the job.


### Installing and testing ML models

Now, just like in the [backend server's README](../backend/README.md) complete the backend installation by running the `make` commands:

```bash
make install-requirements  # basically just `pip install`
make install-all-models    # many `git clone` and `wget` for models and ckpts
```

Create the `.env` file based on the `.env.example` and fill out your Huggingface token. Set the `.env` file to be private to you, so that nobody can steal your token. Then make sure you have pull access to LLaMa and Sign2Vec from your huggingface account (if not, you will get a message when you test models and you can debug from there). Then test the models to perform all huggingface pulls AND to test inference:

```bash
# setup the .env
cp .env.example .env
chmod 600 .env

# fill out your HF token
nano .env

# tests all models (plus triggers huggingface downloads)
make test-all-models
```

The models tests should finish without crashing. If an exception appears, or a huggingface complaint about repository access appears, you need to resolve the issue.

You can run each test individually to debug the source of the issue:

```bash
# for example Sign2Vec
.venv/bin/python3 -m app.debug.test_s2v
```

Once all tests pass, you can safely start the backend server, knowing it is unlikely it will crash during runtime.


### Starting the backend server

Congratulations! Now you can start the server like this:

```bash
make start
```

The `uvicorn` server will be started on port `1817`, waiting for incomming HTTP requests:

```
INFO:     Will watch for changes in these directories: ['/home/clsp-mayer/jsalt/demo/backend']
INFO:     Uvicorn running on http://127.0.0.1:1817 (Press CTRL+C to quit)
INFO:     Started reloader process [1236247] using WatchFiles
```

You kill it by pressing `Ctrl + C`.

> **Note:** On my laptop, running `make start` watches for changes in the `.py` files and when one occurs it reloads the server. On rockfish (despite the logs stating the oposie), this behavior seems to be broken, so you need to manually kill and start the server whenever you make a change to the backend code.


## Setting up the SSH tunnel

Running the backend server is only the first part of the setup. Next we need to tunnel the port 1817 via SSH from your laptop, through a login node, into the running job. This is so that typing http://localhost:1817 into your browser actually accesses the running backend server.

Start by running the `laptop -> login node` port forward first, because we don't have control over which login we connect to when we are outside the Rocfish cluster. Run this command in a new terminal from your laptop:

```bash
# we are at:
# jirka@my-laptop:~$

ssh -L 1817:localhost:1817 clsp-mayer@login.rockfish.jhu.edu
```

After typing in the password you will get a shell on some login node. Remember the node name, we will use it later. I got connected to `login01`.

Now we need to start the other half of the tunnel - from the running job, into the `login01` node. But this time, we open the tunnel from the other end (see the first diagram, we open the tunnel from the tip of the arrow, not the base), so there's a sligtly different command to be used. Run this command from the interactive GPU job that you used to setup the backend server before:

```bash
# we are at:
# [clsp-mayer@gpu13 backend]$

# replace login01 with the specific head node number the first tunnel openned to
ssh -NR 1817:localhost:1817 login01 &
```

The last ampersand (`&`) makes sure the command runs in the background, so that we still have access to the shell to run the backend server.

Now start the backend server:

```bash
# we are at:
# [clsp-mayer@gpu13 backend]$

make start
```

Now if you open the browser on your laptop and open http://localhost:1817, you should see the welcome page of the backend server.

If this works, you have your backend set up and you can move on to set up the frontend on your laptop.

Let me put the diagram here again:

<img src="img/rockfish-ssh-setup.svg" alt="Diagram of the Rockfish setup with the SSH tunnel" />


### Quality of life commands for the SHH tunnel

The two halves of the SSH tunnel can be started independently, but they need to meet at the same login node in order to work.

The first half tunnels your browser HTTP request into the login node, where it appears as-if the browser was actually running on the login node itself (that's why there are those `localhost`s everywhere - each jump between processes happens inside a single machine). The second half tunnels this request further into the `gpu13` machine where the backend server acually runs. So the end result is a setup where the browser thinks the backend server is running on your laptop, and the backend server thinks it's getting requests from a browser running on the `gpu13` machine (i.e. the localhost).

When you try to start one of the commands and you get an error that the port is already occupied, chances are you are already running that command in some terminal somewhere. On your local laptop, just go through all terminals and kill that other process.

The other clash can happen inside the interactive GPU job. If that happens, try running the `ps` command to see all the processes you've started:

```
    PID TTY          TIME CMD
  55017 pts/0    00:00:00 bash
1270375 pts/0    00:00:00 ssh
1270376 pts/0    00:00:00 ps
```

You can see the `ssh` command running with the process ID `1270375`. It's running in the background because we started the `ssh` with the ampersand (`&`) at the end. You need to kill that command manually:

```bash
kill 1270375
```

> **Note:** Stopping the slurm job will send a cascade of interrupt/kill commands to all child processes, which will also terminate the `ssh` process. Don't worry about polluting the `gpu13` machine with free-roaming processes.


## Setting up frontend

Running frontend from your laptop requires only installing `Node.js` and then starting the frontend hosting server via the `npm run start` command. All of this is described in the [Frontend README file](../frontend/README.md).

Once that's set up, the frontend application is configured to access the `localhost:1817` endpoint whenever it itself is running on `localhost:1234`, therefore if the SSH tunnel is in place, everything should be working.

Check that the SSH tunnel did not become frozen or stuck and restart it if so. Sometimes temporary network outages cause the tunnel to break (at least the laptop-to-login half). If you can access the backend via browser, the frontend should as well.


## Managing conda environments

Before using conda, you need to first activate the `anaconda` module. This must be done from the login node - it does not work inside a running job.

```bash
module load anaconda
```

> **Note:** This command sets the `$PATH` variable to something like `/data/apps/...centos.../..gcc../...anaconda.../bin`, where these cluster-wide apps are installed.

You can verify that the `conda` command works:

```bash
conda -V
```

You can list the existing conda environments:

```bash
conda info --envs
```

> **Note:** There are a few pre-defined environments, such as `jupyter` or `ant-1.6.0`. We don't care about these. Our own environments have paths that lead into our home directory into the `/home/clsp-mayer/.conda/envs` folder.

We want to create an empty conda environment, where we only specify the python version. We don't need any pip packages or any other thing - those will be installed into the `.venv` folder we create later.

```bash
conda create --name signllava-demo python=3.10
```

Listing the environments again should show the environment being present.

You can activate the new conda environment like this:

```bash
conda activate signllava-demo
```

This changes the prompt to the following:

```
(signllava-demo) [clsp-mayer@login01 ~]$
```

You can verify that the `python3` command now actually points to our conda environment's python executable by running:

```bash
which python3
```

You should get a response like:

```
~/.conda/envs/signllava-demo/bin/python3
```

You can see that it points inside our `signllava-demo` environment.

Now we are ready to use the `python3` command to create our virtual environment for the backend server.

Later, when you want to uninstall the whole setup, you can remove the conda environment by running:

```bash
conda remove --name signllava-demo --all
```
