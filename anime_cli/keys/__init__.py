# Copyright (c) 2022-2024 iiPython

# Modules
import os
from . import keys  # noqa: F401

if os.name == "nt":
    from .read_win import readchar  # noqa: F401

elif "ix" in os.name:
    from .read_linux import readchar  # noqa: F401
