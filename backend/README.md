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


## Installing Mediapipe

Clone the PoseEstimation repo into the `models` directory.

```bash
cd models
git clone git@github.com:JSALT2024/PoseEstimation.git
cd ..
```

The project is not a python package, so it cannot be installed via pip. Instead, the `sys.path.append("...")` method is used to import it.

Now, download the trained model in `checkpoints/PoseEstimation`:

```bash
mkdir -p checkpoints/PoseEstimation
wget -O checkpoints/PoseEstimation/hand_landmarker.task -q https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task
wget -O checkpoints/PoseEstimation/pose_landmarker_full.task -q https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_full/float16/latest/pose_landmarker_full.task
wget -O checkpoints/PoseEstimation/face_landmarker.task -q https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/latest/face_landmarker.task
```


## Installing MAE encoder

Clone the MAE repo into the `models` directory.

```bash
cd models
git clone git@github.com:JSALT2024/MAE.git
cd MAE
git checkout video_mae
git pull
cd ../..
```

The project is not a python package, so it cannot be installed via pip. Instead, the `sys.path.append("...")` method is used to import it.

Now, download the trained model into `checkpoints/MAE`:

```bash
# create the dir (and/or symlink it to some cluster storage mountpoint, since theres going to be more data present here)
mkdir -p checkpoints/MAE

# download if not downloaded already
wget -nc https://github.com/JSALT2024/MAE/releases/download/mae_model/vit_base_16_16-07_21-52-12_checkpoint-440.pth -P checkpoints/MAE
```

You can test the MAE encoder by running:

```bash
.venv/bin/python3 -m app.debug.test_mae
```


## Installing Sign2Vec encoder

Clone the Sign2Vec repo into the `models` folder:

```bash
cd models
git clone git@github.com:JSALT2024/sign2vec.git
cd sign2vec
git checkout pretraining --
git pull
cd ../..
```

The project is not a python package, so it cannot be installed via pip. Instead, the `sys.path.append("...")` method is used to import it.

The model checkpoint will be downloaded from huggingface.


## Installing Dino encoder

Clone the DINO repo into the `models` folder:

```bash
cd models
git clone git@github.com:JSALT2024/DINOv2.git
cd ..
```

The project is not a python package, so it cannot be installed via pip. Instead, the `sys.path.append("...")` method is used to import it.

Now, download the trained model(s) into the `checkpoints` folder:

```bash
# create the dir (and/or symlink it to some cluster storage mountpoint, since theres going to be more data present here)
mkdir -p checkpoints/DINOv2

# download if not downloaded already
wget -nc https://github.com/JSALT2024/DINOv2/releases/download/dinov2_model/face_dinov2_vits14_reg_teacher_checkpoint.pth -P checkpoints/DINOv2
wget -nc https://github.com/JSALT2024/DINOv2/releases/download/dinov2_model/hand_dinov2_vits14_reg_teacher_checkpoint.pth -P checkpoints/DINOv2
```

You can test the DINO encoder by running:

```bash
.venv/bin/python3 -m app.debug.test_dino
```
