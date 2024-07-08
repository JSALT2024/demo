from llava.sign_public_api import SignLlava, SignLlavaInput, SignLlavaOutput


def test_sign_llava():
    print(SignLlava)
    print("TODO...")

    # TODO: use the model, something like this:
    our_model = SignLlava.load_from_checkpoint("xuan/sign-llava-80")
    my_input = SignLlavaInput("asdasd", "....")
    my_output = our_model.run_inference(my_input)

    print(my_output.text)
    print(my_output.text_embeddings)
    print(my_output.projected_mae_embeddings)


if __name__ == "__main__":
    test_sign_llava()
