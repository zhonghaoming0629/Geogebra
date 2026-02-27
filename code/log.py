from const import *
from datetime import datetime
import os

def log(text, type="Normal"):
    now = str(datetime.now().year) + str(datetime.now().month)
    with open(os.path.join(BASIC_PATH, f"logs/log{now}.log"), "a+") as f:
        f.write(f"{type}:{now} {text}\n")
    pass