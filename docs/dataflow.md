# Dataflow

After a video is uploaded, it is processed by the [`VideoProcessor`](../backend/app/services/VideoProcessor.py) class. The processor operates entirely in a so-called "video folder", which is a folder at `backend/storage/video_data/{video-id}`. In this folder, the processor gets the uploaded video file and starts processing. It produces a number of files and folders captured in the following diagram:

<img src="img/dataflow.svg" alt="How is all the data about a video computed" />

If you want to know the details of the specific data format, it can be gauged from the source code of the corresponding processor that produces that data, or from the datatype definition (there are `assert`s in constructors).

For example, looking at the [`MaeProcessor`](../backend/app/encoding/MaeProcessor.py) we can see the that `visual_features` matrix created at the beginning and later stored as `mae_features.npy` has the shape `(total_frames, MAE_FEATURES_DIMENSION)` and dtype `np.float32`.

Similarly the [`MediapipeProcessor`](../backend/app/preprocessing/MediapipeProcessor.py) produces one [`FrameGeometry`](../backend/app/domain/FrameGeometry.py) instance for each video frame. The `FrameGeometry.__post_init__` method performs all the checks that hold for the data produced by the model. The comments for individual fields describe the meaning of those fields and the edgecase behavior.
