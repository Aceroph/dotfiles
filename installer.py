from curses import wrapper
from pathlib import Path
import curses
import os


CONTROLS = ["quit", "install", "delete"]
BAR_SPACING = 1
TITLE = "Dotfiles Manager"


class Installer:
    def __init__(self):
        self.index = 0

        self.installed = []
        self.existing = []

        self.configs = os.listdir(str(Path(__file__).parent / "configs"))
        self.scripts = os.listdir(str(Path(__file__).parent / "scripts"))
        self.get_installed()


    def get_installed(self):
        self.installed.clear()
        self.existing.clear()
        for file in self.configs:
            config_path = Path.home() / ".config" / file
            script_path = Path("/usr/local/bin") / file

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
            
            # Configs
            stdscr.addstr(0, 0, "Configs", curses.color_pair(1))
            if len(self.configs) == 0:
                stdscr.addstr(1, 0, "No config found")
            for i, name in enumerate(self.configs):
                stdscr.addstr(i + 1, 0, name, curses.A_STANDOUT * (i == self.index))

                if name in self.installed:
                    stdscr.addstr(i + 1, 20, "(Installed)", curses.color_pair(2))
                elif name in self.existing:
                    stdscr.addstr(i + 1, 20, "(Existing)", curses.color_pair(3))
            
            # Scripts
            scripts_offset_y = max(len(self.configs), 1) + 2
            stdscr.addstr(scripts_offset_y, 0, "Scripts", curses.color_pair(1))
            if len(self.scripts) == 0:
                stdscr.addstr(scripts_offset_y + 1, 0, "No scripts found")
            for i, name in enumerate(self.scripts):
                stdscr.addstr(scripts_offset_y + 1, 0, name, curses.A_STANDOUT * i + len(self.configs) == self.index)
                
                if name in self.installed:
                    stdscr.addstr(scripts_offset_y + 1, 20, "(Installed)", curses.color_pair(2))
                elif name in self.existing:
                    stdscr.addstr(scripts_offset_y + 1, 20, "(Existing)", curses.color_pair(3))

            # Render tool bar
            bar_offset_x = 0
            for ctrl in CONTROLS:
                stdscr.addstr(rows - 1, bar_offset_x, ctrl[0], curses.A_STANDOUT ^ curses.A_UNDERLINE)
                stdscr.addstr(rows - 1, bar_offset_x + 1, ctrl[1:].ljust(len(ctrl) + BAR_SPACING), curses.A_STANDOUT)
                bar_offset_x += len(ctrl) + BAR_SPACING

            stdscr.addstr(rows - 1, bar_offset_x, " ".ljust(cols - bar_offset_x - 1), curses.A_STANDOUT)
            stdscr.addstr(rows - 1, cols - len(TITLE) - 1, TITLE, curses.A_STANDOUT)
        
            key = stdscr.getch()
            file = None
            if self.index < len(self.configs) and len(self.configs) > 0:
                file = self.configs[self.index]
            elif self.index - len(self.configs) < len(self.scripts):
                file = self.scripts[self.index - len(self.configs)]
            target = Path.home() / ".config"

            if key == ord('q'):
                break

            elif key == ord('i') and file:
                source = Path(__file__).parent / "configs" / file
                os.system(f"rm -rf {target / file}")
                os.system(f"ln -s {source} {target}")
                self.get_installed()

            elif key == ord('d') and file:
                os.system(f"rm -rf {target / file}")
                self.get_installed()
            
            elif key == curses.KEY_UP and self.index > 0:
                self.index -= 1

            elif key == curses.KEY_DOWN and self.index < len(self.configs) + len(self.scripts):
                self.index += 1

            stdscr.refresh()

if __name__ == "__main__":
    installer = Installer()
    wrapper(installer.main)
