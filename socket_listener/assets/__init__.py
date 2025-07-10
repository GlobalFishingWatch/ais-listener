from importlib.resources import files


def get_sample_data_path(path: str):
    return files("socket_listener.assets.sample_data").joinpath(path)
