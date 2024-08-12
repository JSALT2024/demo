####################
# General commands #
####################

.PHONY: install-requirements start start-production

install-requirements:
	.venv/bin/python3 -m pip install --upgrade pip
	.venv/bin/python3 -m pip install -r requirements.txt

start:
	.venv/bin/python3 -m uvicorn app.api.main:app --port 1817 --reload

start-production:
	.venv/bin/python3 -m uvicorn app.api.main:app --host 0.0.0.0 --port 1817


#########################################
# Installing ML models used by the demo #
#########################################

.PHONY: install-ffmpeg install-all-models install-mediapipe install-mae install-dino install-s2v install-sign-llava

install-all-models: install-ffmpeg install-mediapipe install-mae install-dino install-s2v install-sign-llava

install-ffmpeg:
	mkdir -p models
	rm -rf models/ffmpeg
	mkdir -p models/ffmpeg
	cd models/ffmpeg; wget https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz
	cd models/ffmpeg; tar xf ffmpeg-release-amd64-static.tar.xz
	rm -rf .venv/bin/ffmpeg .venv/bin/ffprobe
	ln -s ../../models/ffmpeg/ffmpeg-7.0.1-amd64-static/ffmpeg .venv/bin/ffmpeg
	ln -s ../../models/ffmpeg/ffmpeg-7.0.1-amd64-static/ffprobe .venv/bin/ffprobe

install-mediapipe:
	mkdir -p models
	rm -rf models/PoseEstimation
	cd models; git clone git@github.com:JSALT2024/PoseEstimation.git
	cd models/PoseEstimation; git reset --hard 575b130c7d2797d4d845abcd759caffc25822e75
	rm -rf checkpoints/PoseEstimation
	mkdir -p checkpoints/PoseEstimation
	wget -O checkpoints/PoseEstimation/hand_landmarker.task -q https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task
	wget -O checkpoints/PoseEstimation/pose_landmarker_full.task -q https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_full/float16/latest/pose_landmarker_full.task
	wget -O checkpoints/PoseEstimation/face_landmarker.task -q https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/latest/face_landmarker.task

install-mae:
	mkdir -p models
	rm -rf models/MAE
	cd models; git clone git@github.com:JSALT2024/MAE.git
	cd models/MAE; git reset --hard f887da09488559a00b937e56d908659b5cf4bdf0
	rm -rf checkpoints/MAE
	mkdir -p checkpoints/MAE
	wget -nc https://github.com/JSALT2024/MAE/releases/download/mae_model/vit_base_16_16-07_21-52-12_checkpoint-440.pth -P checkpoints/MAE

install-dino:
	mkdir -p models
	rm -rf models/DINOv2
	cd models; git clone git@github.com:JSALT2024/DINOv2.git
	cd models/DINOv2; git reset --hard b6a61b7b9632a311e18e15a507e157e65e8b6cb8
	rm -rf checkpoints/DINOv2
	mkdir -p checkpoints/DINOv2
	wget -nc https://github.com/JSALT2024/DINOv2/releases/download/dinov2_model/face_dinov2_vits14_reg_teacher_checkpoint.pth -P checkpoints/DINOv2
	wget -nc https://github.com/JSALT2024/DINOv2/releases/download/dinov2_model/hand_dinov2_vits14_reg_teacher_checkpoint.pth -P checkpoints/DINOv2

install-s2v:
	mkdir -p models
	rm -rf models/sign2vec
	cd models; git clone git@github.com:JSALT2024/sign2vec.git
	cd models/sign2vec; git reset --hard 2395fe0759c4e8510ebc665c406e185d582baf7d

install-sign-llava:
	rm -rf models/Sign_LLaVA
	git clone git@github.com:JSALT2024/Sign_LLaVA.git models/Sign_LLaVA
	(cd models/Sign_LLaVA && git reset --hard 19cd35769b898517e2eacbbebaa4791cb84e000d)
	.venv/bin/python3 -m pip install --no-deps --editable ./models/Sign_LLaVA
	rm -rf checkpoints/Sign_LLaVA
	mkdir -p checkpoints/Sign_LLaVA
	(cd checkpoints/Sign_LLaVA && wget "https://github.com/JSALT2024/Sign_LLaVA/releases/download/checkpoint/test_ckpt_July_26_2024_11am.zip")
	(cd checkpoints/Sign_LLaVA && unzip test_ckpt_July_26_2024_11am.zip)
	mv checkpoints/Sign_LLaVA/test_ckpt_July_26_2024_11am/* checkpoints/Sign_LLaVA/

test-all-models:
	@echo "TESTING FFMPEG..."
	.venv/bin/python3 -m app.debug.test_ffmpeg
	@echo "TESTING MEDIAPIPE..."
	.venv/bin/python3 -m app.debug.test_mediapipe
	@echo "TESTING MAE..."
	.venv/bin/python3 -m app.debug.test_mae
	@echo "TESTING DINO..."
	.venv/bin/python3 -m app.debug.test_dino
	@echo "TESTING SIGN2VEC..."
	.venv/bin/python3 -m app.debug.test_s2v
	@echo "TESTING SIGN_LLAVA"
	.venv/bin/python3 -m app.debug.test_sign_llava
	@echo ========================
	@echo SUCCESS!
