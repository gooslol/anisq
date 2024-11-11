# Copyright (c) 2024 iiPython

# Modules
import sys
import typing

from .keys import readchar, keys

# Main menu class
class MenuHandler(object):
    def show(self, options: list[tuple]) -> typing.Any:
        options.append((None, "<-- Go Back"))
        iterated, length, index = 0, len(options), 0
        while True:
            sys.stdout.write(f"\033[{length}F" * iterated)

            # Handle control
            if iterated:
                key = readchar()
                if key in [keys.UP, "w"]:
                    index = length - 1 if index - 1 < 0 else index - 1

                elif key in [keys.DOWN, "s"]:
                    index = 0 if index + 1 >= length else index + 1

                elif key == keys.ENTER:
                    sys.stdout.write("\n")
                    return options[index][0]

                elif key == keys.CTRL_C:
                    raise KeyboardInterrupt

            # Print out options
            for i, option in enumerate(options):
                option_text = f"\033[33m{option[1]}\033[0m" if i == index else option[1]
                sys.stdout.write(f"\033[2K  \033[34m{i + 1}\033[0m\t{option_text}\n")

            iterated = 1

menu = MenuHandler()
