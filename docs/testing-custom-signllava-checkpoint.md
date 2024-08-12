# Testing custom SignLLaVA checkpoint

If you train a custom SignLLaVA model and you want to test it in the demo, there are two options:


## 1. Perform a proper deployment

You zip the checkpoints and create a [GitHub release](https://github.com/JSALT2024/Sign_LLaVA/releases) with the checkpoint attached. You create an install script (just copy an install script of an older release and modify the URLs). You then run the install script in the `backend` folder to perform the install. Run the `python3 -m app.debug.test_sign_llava` test to check the model and then restart the backend server to re-load the LLM.

To make the change a proper deployment, modify the `Makefile`, the `install-sign-llava` block and copy the install script there.


## 2. Perform a quick check only, no commits, no deployment

Assuming you have the checkpoint stored somewhere in the filesystem where you run the demo backend server, you can just open [`SignLlavaCache`](../backend/app/translation/SignLlavaCache.py) and modify the `SIGN_LLAVA_CHECKPOINT` constant to make it point to your checkpoint. And restart the backend server. Make sure NOT to commit this change accidentally, though.

Optionally, you can temporarily patch the `backend/models/Sign_LLaVA` source code to debug. Although, you are almost better off doing a proper release if you need to change the model source code to make it work.

The next step would be going through the install code (`Makefile` the block `install-sign-llava`), understanding that, and then reading the `test_sign_llava.py` debug code and understanding that and that should allow you to play with the integration more and debug more complex changes to the LLM.
