import os
import sys


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    # return 'F:\project\manufactor\Version\V_9\code\\' + relative_path
    return os.path.join(base_path, relative_path)
