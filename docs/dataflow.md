# Dataflow

What data in what shapes *exactly* flows through the application.


## Video

The initial input is a video file with a signer. The video is an `mp4` or `webm` or some other well-known video format that can be loaded by common video processing libraries.

> **Note:** Streaming is currently suspended for after the batch processing, because there are lots of pitfalls to be figured out and lots to be read and understood. Most likely it will be implemented by batch processing of 10s video chunks.

The first step is video preprocessing, that normalizes the video framerate to cca 30 FPS and reduces the resolution to max 512 pixels in the smaller dimension.

If the video is too long, it needs to be sliced up into chunks called "clips". This is because:

- the LLaMA model has a finite context size, which cannot fit the entire video, thus we do the autoregressive translation
- sign2vec also has a limitation on the maximum input length


## Mediapipe

> **Repository:** https://github.com/JSALT2024/PoseEstimation

After the video is preprocessed, the pose of the signer is detected in the whole video. It is aggregated over the whole video to estimate the signing space square.

Then the video is cropped to become a square, where the signer sits in the center of the signing space. Area not covered by the video has the ImageNet average gray color.


## Encoders

### MAE

> **Repository:** https://github.com/JSALT2024/MAE/tree/video_mae

The square video is fed frame-by-frame into MAE. The input frame has shape `(224, 224, 3)` where the dimensions are `(width ??, height ??, rgb ??)` (check this!!!).

- ImageNet normalization? float32 or uint8?

The MAE input allows batching for more performance, so an additional batch channel is added as the first dimension.

The MAE produces a single vector as an output of size `???`.


### Sign2Vec

> **Repository:** https://huggingface.co/karahansahin/sign2vec-v1-how2sign

The pose data from mediapipe is fed into the sign2vec model. The joint coordinates can be in any coordinate system, because the spotter2 loader (part of sign2vec) rescales based on the shoulder distance.

- What coordinate system should be used for joints when they are fed into sign2vec? Does spotter2 resolve this as well? Vertical flip? Horizontal flip?
- What joints should be passed in what order? Joint coords in XY or YX order?


### DINO

TODO: Talk to Schester.


## Sign LLaVA

- Translation clip-by-clip
- Chatting
- Projected embedding visualization
