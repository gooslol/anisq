# Copyright (c) 2024-2025 iiPython

# Modules
import sys

from readchar import readkey, key

# Main menu class
class MenuHandler:
    def show(self, options: list[tuple]) -> tuple:
        options.append(("<-- Go Back", None))
        iterated, length, index = 0, len(options), 0
        while True:
            sys.stdout.write(f"\033[{length}F" * iterated)

            # Handle control
            if iterated:
                match readkey():
                    case key.UP | "w":
                        index = length - 1 if index - 1 < 0 else index - 1

                    case key.DOWN | "s":
                        index = 0 if index + 1 >= length else index + 1

                    case key.ENTER:
                        sys.stdout.write("\n")
                        return options[index]

                    case key.CTRL_C:
                        raise KeyboardInterrupt

            # Print out options
            for i, option in enumerate(options):
                option_text = f"\033[33m{option[0]}\033[0m" if i == index else option[0]
                sys.stdout.write(f"\033[2K  \033[34m{i + 1}\033[0m\t{option_text}\n")

            iterated = 1

menu = MenuHandler()
