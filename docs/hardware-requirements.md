# Hardware requirements

## Memory usage

I measured the peak memory usage for the debug tests of all used models on a machine with the A100 GPU (a quarter partition with 40GB memory only) with 45GB RAM allocation.

| `app.debug.`     | Peak GPU    | Peak RAM |
| ---------------- | ----------- | -------- |
| `test_ffmpeg`    |  CPU only   |   `700M` |
| `test_mediapipe` |  `1_760MiB` | `9_500M` |
| `test_mae`       |  `2_500MiB` | `5_700M` |
| `test_dino`      |  `2_350MiB` | `5_660M` |
| `test_s2v`       |  CPU only   | `1_750M` |
| `sign_llava`     | `22_000MiB` | `7_500M` |


### Conclusions

- I can keep the LLM loaded in GPU memory so that it runs fast when requested.
- The GPU should have at least 30 GB of memory.
    - Though can be 24 GB without parallel model execution.
- Mediapipe is RAM intensive! 10GB per worker!
- The machine should have 32GB of RAM to run 2 mediaipe workers.
    - Then +10 for each new worker.


## How the measurement was done

I get an interactive job running in slurm. From another terminal I SSH into the same machine and run `watch -n 0.1 nvidia-smi` to see the GPU memory usage.

To measure RAM usage, open up `htop -d 0.1`, sort by `PID` (or `USER`) to get the latest processes and watch for the test process. The `RES` column shows the total RAM usage.
