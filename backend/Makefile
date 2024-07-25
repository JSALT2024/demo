####################
# General commands #
####################

.PHONY: install-requirements start start-production

install-requirements:
	.venv/bin/pip3 install --upgrade pip
	.venv/bin/pip3 install -r requirements.txt

start:
	.venv/bin/python3 -m uvicorn app.api.main:app --port 1817 --reload

start-production:
	.venv/bin/python3 -m uvicorn app.api.main:app --host 0.0.0.0 --port 1817


#########################################
# Installing ML models used by the demo #
#########################################

.PHONY: install-all-models install-sign-llava install-mediapipe install-mae install-dino install-s2v

install-all-models: install-sign-llava install-mediapipe install-mae install-dino install-s2v

# TODO: freeze a specific commit ID instead of branch
# install-sign-llava:
# 	mkdir -p models
# 	rm -rf models/Sign_LLaVA
# 	cd models; git clone git@github.com:JSALT2024/Sign_LLaVA.git
# 	cd models/Sign_LLaVA; git checkout multi_task
# 	cd models/Sign_LLaVA; git pull
# 	rm -rf checkpoints/Sign_LLaVA
# 	mkdir -p checkpoints/Sign_LLaVA
# TODO: pip install the package!

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
