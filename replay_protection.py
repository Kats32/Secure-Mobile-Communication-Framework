"""Small replay-counter policy shared by the server and its checks."""


def is_replay(counter, last_counter):
    """Return whether counter is invalid or not newer than last_counter."""
    if type(counter) is not int or counter < 1:
        return True
    return counter <= last_counter
