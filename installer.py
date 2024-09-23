from curses import wrapper
from pathlib import Path
import curses
import os


CONTROLS = ["quit", "install", "delete"]
BAR_SPACING = 1
TITLE = "Dotfiles Manager"

SCRIPT_PATH = Path("/usr/local/bin/")
CONFIG_PATH = Path.home() / ".config"


class Installer:
    def __init__(self):
        self.index = 0

        self.scriptcount = 0
        self.configcount = 0

        self.installed = []
        self.existing = []

        self.files = {}
        for file in os.listdir(str(Path(__file__).parent / "configs")):
            self.files[file] = "config"
            self.configcount += 1

        for file in os.listdir(str(Path(__file__).parent / "scripts")):
            self.files[file] = "script"
            self.scriptcount += 1

        self.get_installed()


    def get_installed(self):
        self.installed.clear()
        self.existing.clear()
        for file in self.files.keys():
            config_path = CONFIG_PATH / file
            script_path = SCRIPT_PATH / file

            if config_path.exists() or script_path.exists():
                if config_path.is_symlink() or script_path.is_symlink():
                    self.installed.append(file)
                else:
                    self.existing.append(file)


    def main(self, stdscr):
        curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)

        while True:
            stdscr.clear()
            rows, cols = stdscr.getmaxyx()
            
            # Labels
            stdscr.addstr(0, 0, "Configs", curses.color_pair(1))
            stdscr.addstr(self.configcount + 2, 0, "Scripts", curses.color_pair(1))

            # List files
            for i, file in enumerate(self.files.items()):
                name, kind = file
                offset_y = 1 if kind == "config" else 3

                stdscr.addstr(i + offset_y, 0, name, curses.A_STANDOUT * (i == self.index))

                if name in self.installed:
                    stdscr.addstr(i + offset_y, 20, "(Installed)", curses.color_pair(2))
                elif name in self.existing:
                    stdscr.addstr(i + offset_y, 20, "(Existing)", curses.color_pair(3))
            
            # Render tool bar
            bar_offset_x = 0
            for ctrl in CONTROLS:
                stdscr.addstr(rows - 1, bar_offset_x, ctrl[0], curses.A_STANDOUT ^ curses.A_UNDERLINE)
                stdscr.addstr(rows - 1, bar_offset_x + 1, ctrl[1:].ljust(len(ctrl) + BAR_SPACING), curses.A_STANDOUT)
                bar_offset_x += len(ctrl) + BAR_SPACING

            stdscr.addstr(rows - 1, bar_offset_x, " ".ljust(cols - bar_offset_x - 1), curses.A_STANDOUT)
            stdscr.addstr(rows - 1, cols - len(TITLE) - 1, TITLE, curses.A_STANDOUT)
            
            # Get selected file
            file = list(self.files.keys())[self.index]
            kind = list(self.files.values())[self.index]

            target = CONFIG_PATH if kind == "config" else SCRIPT_PATH

            # Process keys
            key = stdscr.getch()
            if key == ord('q'):
                break

            elif key == ord('i'):
                match kind:
                    case "script":
                        source = Path(__file__).parent / "scripts" / file
                        os.system(f"sudo rm -rf {target / file}")
                        os.system(f"sudo ln -s {source} {target}")
                    case "config":
                        source = Path(__file__).parent / "configs" / file
                        os.system(f"rm -rf {target / file}")
                        os.system(f"ln -s {source} {target}")
                self.get_installed()

            elif key == ord('d'):
                match kind:
                    case "script":
                        os.system(f"sudo rm -rf {target / file}")
                    case "config":
                        os.system(f"rm -rf {target / file}")
                self.get_installed()
            
            elif key == curses.KEY_UP and self.index > 0:
                self.index -= 1

            elif key == curses.KEY_DOWN and self.index < len(self.files.keys()):
                self.index += 1

            stdscr.refresh()

if __name__ == "__main__":
    installer = Installer()
    wrapper(installer.main)
