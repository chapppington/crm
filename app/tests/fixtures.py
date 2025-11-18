from punq import Container

from application.container import _init_container


def init_dummy_container() -> Container:
    container = _init_container()

    return container
