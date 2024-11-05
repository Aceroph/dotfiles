from curses import wrapper
from typing import Tuple
from pathlib import Path
import curses
import os


CONTROLS = ["quit", "install", "delete", "save"]
BAR_SPACING = 1
TITLE = "Dotfiles Manager"

SCRIPT_PATH = Path("/usr/local/bin/")
CONFIG_PATH = Path.home() / ".config"
LOCAL_CONFIG_PATH = Path(__file__).parent / "configs"
LOCAL_SCRIPT_PATH = Path(__file__).parent / "scripts"


class Type:
    CONFIG = 0
    SCRIPT = 1


class Installer:
    def __init__(self):
        self.index = 0
        self.offset = 0

        self.files = {}
        unique = []
        # /home/user/.config
        for file in CONFIG_PATH.glob("*"):
            self.files[file] = Type.CONFIG
            unique.append(file.name)

        # dotfiles/configs
        for file in LOCAL_CONFIG_PATH.glob("*"):
            if file.name not in unique:
                self.files[file] = Type.CONFIG

        # /usr/local/bin
        for file in SCRIPT_PATH.glob("*"):
            self.files[file] = Type.SCRIPT
            unique.append(file.name)

        # dotfiles/scripts
        for file in LOCAL_SCRIPT_PATH.glob("*"):
            if file.name not in unique:
                self.files[file] = Type.SCRIPT

    def get_state(self, file: Path) -> Tuple[str, int]:
        if os.path.islink(file):
            return "(Saved & synced)", curses.color_pair(2)
        else:
            if file in Path(__file__).parent.glob("*/*"):
                return "(Saved)", curses.color_pair(3)

        return "(Not saved)", 0

    def main(self, stdscr) -> None:
        curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_MAGENTA, curses.COLOR_BLACK)

        while True:
            stdscr.clear()
            rows, cols = stdscr.getmaxyx()

            # Labels
            stdscr.addstr(2, 4, TITLE, curses.color_pair(1))

            # List files
            self.max_items = rows - 6
            files = list(self.files.items())[self.offset : self.offset + self.max_items]
            for i, file in enumerate(files):
                path, kind = file

                match kind:
                    case Type.CONFIG:
                        filetype = "[C]"
                        color = curses.color_pair(2)
                    case Type.SCRIPT:
                        filetype = "[S]"
                        color = curses.color_pair(3)
                    case _:
                        filetype = "[?]"
                        color = curses.color_pair(1)

                stdscr.addstr(i + 4, 0, filetype, color)
                stdscr.addstr(
                    i + 4,
                    4,
                    path.name,
                    curses.A_STANDOUT * (i == self.index - self.offset),
                )

                # State
                state, state_color = self.get_state(path)
                stdscr.addstr(
                    i + 4,
                    cols - 30,
                    state,
                    state_color | curses.A_UNDERLINE * (i == self.index - self.offset),
                )

            # Render tool bar
            bar_offset_x = 0
            for ctrl in CONTROLS:
                stdscr.addstr(
                    rows - 1,
                    bar_offset_x,
                    ctrl[0],
                    curses.A_STANDOUT ^ curses.A_UNDERLINE,
                )
                stdscr.addstr(
                    rows - 1,
                    bar_offset_x + 1,
                    ctrl[1:].ljust(len(ctrl) + BAR_SPACING),
                    curses.A_STANDOUT,
                )
                bar_offset_x += len(ctrl) + BAR_SPACING

            stdscr.addstr(
                rows - 1,
                bar_offset_x,
                " ".ljust(cols - bar_offset_x - 1),
                curses.A_STANDOUT,
            )

            # Show current index at the end of the tool bar
            stdscr.addstr(
                rows - 1,
                cols - 6,
                f"{self.index + 1:02}/{len(self.files.items()):02}",
                curses.A_STANDOUT,
            )

            # Get selected file
            file = list(self.files.keys())[self.index]
            kind = list(self.files.values())[self.index]

            target = CONFIG_PATH if kind == Type.CONFIG else SCRIPT_PATH

            # Process keys
            key = stdscr.getch()
            match chr(key):
                case "q":
                    break

                case "i":
                    match kind:
                        case Type.SCRIPT:
                            source = LOCAL_SCRIPT_PATH / file.name
                            os.system(f"sudo rm -rf {target / file.name}")
                            os.system(f"sudo ln -s {source} {target}")
                        case Type.CONFIG:
                            source = LOCAL_CONFIG_PATH / file.name
                            os.system(f"rm -rf {target / file.name}")
                            os.system(f"ln -s {source} {target}")

                case "d":
                    match kind:
                        case Type.SCRIPT:
                            os.system(f"sudo rm -rf {target / file.name}")
                        case Type.CONFIG:
                            os.system(f"rm -rf {target / file.name}")

                case "s":
                    match kind:
                        case Type.SCRIPT:
                            source = LOCAL_SCRIPT_PATH / file.name
                            os.system(f"mv {target / file.name} {source}")
                            os.system(f"sudo rm -rf {target / file.name}")
                            os.system(f"sudo ln -s {source} {target}")
                        case Type.CONFIG:
                            source = LOCAL_CONFIG_PATH / file.name
                            os.system(f"mv {target / file.name} {source}")
                            os.system(f"rm -rf {target / file.name}")
                            os.system(f"ln -s {source} {target}")

                case "ă":
                    self.index = max(0, self.index - 1)

                    # Offset up
                    if self.index < self.offset:
                        self.offset -= 1

                case "Ă":
                    self.index = min(len(self.files) - 1, self.index + 1)

                    # Offset down
                    if self.index >= self.offset + self.max_items:
                        self.offset += 1

            stdscr.refresh()


if __name__ == "__main__":
    installer = Installer()
    wrapper(installer.main)
