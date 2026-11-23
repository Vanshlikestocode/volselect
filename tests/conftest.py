import os

os.environ.setdefault("VOLSELECT_OFFLINE", "1")  # the live page must not hit the network during tests
