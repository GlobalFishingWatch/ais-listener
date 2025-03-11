"""Package with sink options to publish incoming packets."""
from .pubsub import GooglePubSub

__all__ = [GooglePubSub]


SUBCLASSES_MAP = {
    "google_pubsub": GooglePubSub,
}


def create_sink(name, *args, **kwargs):
    return SUBCLASSES_MAP[name](*args, **kwargs)
