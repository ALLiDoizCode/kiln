"""kiln: turns a reference image and a prompt into a production ready 3D asset."""


class KilnError(Exception):
    """Something kiln cannot go on from, with a message fit to show a person as it is."""
