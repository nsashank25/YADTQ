import curses
import yadtq
import time

class TerminalGUI:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.yadtq_instance = yadtq.YADTQ(broker_ip='127.0.0.1', backend_ip='127.0.0.1')
        self.task_ids = []

        curses.curs_set(0)
        self.stdscr.clear()
        self.stdscr.refresh()

    def add_task(self, task_type, args):
        task_id = self.yadtq_instance.send_task(task_type, args)
        self.task_ids.append(task_id)
        return task_id

    def show_task_status(self):
        while True:
            self.stdscr.clear()
            self.stdscr.addstr(0, 0, "Task Status and Results")
            self.stdscr.addstr(2, 0, "Press 'q' to quit.")
            self.stdscr.addstr(4, 0, "Task ID | Status | Result")

            row = 6
            for task_id in self.task_ids:
                status = self.yadtq_instance.status(task_id)
                result = self.yadtq_instance.value(task_id) if status == "success" else "N/A"
                self.stdscr.addstr(row, 0, f"{task_id} | {status} | {result}")
                row += 1

            self.stdscr.refresh()
            key = self.stdscr.getch()
            if key == ord('q'):
                break
            time.sleep(1)

    def add_task_menu(self):
        while True:
            self.stdscr.clear()
            self.stdscr.addstr(0, 0, "Add a New Task")
            self.stdscr.addstr(2, 0, "Enter task type (add/sub/multiply/divide): ")
            self.stdscr.refresh()

            curses.echo()
            task_type = self.stdscr.getstr(3, 0, 20).decode("utf-8").strip()

            if task_type not in ["add", "sub", "multiply", "divide"]:
                self.stdscr.addstr(5, 0, "Invalid task type! Press any key to try again.")
                self.stdscr.refresh()
                self.stdscr.getch()
                continue

            self.stdscr.addstr(6, 0, "Enter arguments as comma-separated values (e.g. 4, 2): ")
            args_str = self.stdscr.getstr(7, 0, 20).decode("utf-8").strip()

            args_str = args_str.replace(" ", ",")
            try:
                args = list(map(float if task_type == "divide" else int, args_str.split(',')))
            except ValueError:
                self.stdscr.addstr(9, 0, "Invalid input! Ensure the arguments are numbers. Press any key to try again.")
                self.stdscr.refresh()
                self.stdscr.getch()
                continue

            task_id = self.add_task(task_type, args)
            self.stdscr.addstr(11, 0, f"Task submitted with ID: {task_id}. Press 'q' to return to menu.")
            self.stdscr.refresh()

            key = self.stdscr.getch()
            if key == ord('q'):
                break

    def main_menu(self):
        while True:
            self.stdscr.clear()
            self.stdscr.addstr(0, 0, "YADTQ Task Queue - Main Menu")
            self.stdscr.addstr(2, 0, "1. Add Task")
            self.stdscr.addstr(3, 0, "2. View Task Status")
            self.stdscr.addstr(4, 0, "q. Quit")
            self.stdscr.refresh()

            key = self.stdscr.getch()
            if key == ord('1'):
                self.add_task_menu()
            elif key == ord('2'):
                self.show_task_status()
            elif key == ord('q'):
                break

def main(stdscr):
    terminal_gui = TerminalGUI(stdscr)
    terminal_gui.main_menu()

if __name__ == "__main__":
    curses.wrapper(main)

