import os


def add_venv_bin_to_path():
    """
    Calling this function ensures that the .venv/bin folder is present in the
    path environment variable. This function is imdepotent, so you can call
    it repeatedly but it will only add the folder once.
    """
    folder_to_be_added = os.path.join(".venv", "bin")
    variable_value = os.environ["PATH"]
    
    if folder_to_be_added in variable_value:
        return
    
    os.environ["PATH"] += os.pathsep + folder_to_be_added
