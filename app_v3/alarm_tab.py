import sqlite3
import tkinter as tk
from datetime import datetime, timedelta
from pathlib import Path
from tkinter import messagebox, ttk

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

plt.rcParams["font.family"] = "Yu Gothic"
plt.rcParams["axes.unicode_minus"] = False

from alarm_chart import AlarmChart
from alarm_table import AlarmTable
from style import apply_style


# ================================================
# region   Settings
# ================================================
BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "body_inspection_machine.db"

PAGE_TITLE = "■ アラーム別"

# Chart class used by this tab
CHART_CLASS = AlarmChart

# Table class used by this tab
TABLE_CLASS = AlarmTable

# endregion


class AlarmTab(ttk.Frame):

    def __init__(self, parent):
        super().__init__(parent, padding=10)

        # ================================================
        # region   Title frame
        # ================================================
        title_frame = ttk.Frame(self, padding=10)
        title_frame.pack(fill=tk.X)

        ttk.Label(
            title_frame,
            text=PAGE_TITLE,
            style="Title.TLabel",
        ).pack(anchor=tk.W)

        ttk.Separator(title_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=(8, 0))
        # endregion

        # ================================================
        # region   Search frame
        # ================================================
        search_frame = ttk.Frame(
            self,
            padding=10,
        )
        search_frame.pack(
            fill=tk.X,
        )

        ttk.Label(
            search_frame,
            text="Machine No:",
        ).pack(
            side=tk.LEFT,
            padx=5,
        )

        self.machine_combo = ttk.Combobox(
            search_frame,
            width=10,
            state="readonly",
            font=("Yu Gothic", 12),
        )
        self.machine_combo.pack(
            side=tk.LEFT,
            padx=5,
        )
        self.machine_combo.bind(
            "<<ComboboxSelected>>",
            self.search,
        )

        ttk.Label(
            search_frame,
            text="Start:",
        ).pack(
            side=tk.LEFT,
            padx=(20, 5),
        )

        self.start_entry = ttk.Entry(
            search_frame,
            width=12,
            font=("Yu Gothic", 12),
        )
        self.start_entry.pack(
            side=tk.LEFT,
            padx=5,
        )
        self.start_entry.bind(
            "<Return>",
            self.search,
        )
        self.start_entry.bind(
            "<Up>",
            lambda event: self.change_date(self.start_entry, -1),
        )
        self.start_entry.bind(
            "<Down>",
            lambda event: self.change_date(self.start_entry, 1)
        )
        self.start_entry.bind(
            "<Control-Up>",
            lambda event: self.change_month(self.start_entry, -1),
        )
        self.start_entry.bind(
            "<Control-Down>",
            lambda event: self.change_month(self.start_entry, 1),
        )

        ttk.Label(
            search_frame,
            text="End:"
        ).pack(
            side=tk.LEFT,
            padx=(20, 5),
        )

        self.end_entry = ttk.Entry(
            search_frame,
            width=12,
            font=("Yu Gothic", 12),
        )
        self.end_entry.pack(
            side=tk.LEFT,
            padx=5,
        )
        self.end_entry.bind(
            "<Return>",
            self.search,
        )
        self.end_entry.bind(
            "<Up>",
            lambda event: self.change_date(self.end_entry, -1),
        )
        self.end_entry.bind(
            "<Down>",
            lambda event: self.change_date(self.end_entry, 1)
        )
        self.end_entry.bind(
            "<Control-Up>",
            lambda event: self.change_month(self.end_entry, -1),
        )
        self.end_entry.bind(
            "<Control-Down>",
            lambda event: self.change_month(self.end_entry, 1),
        )

        self.search_button = ttk.Button(
            search_frame,
            text="Search",
            command=self.search,
        )
        self.search_button.pack(
            side=tk.LEFT,
            padx=20,
        )
        self.search_button.bind(
            "<Return>",
            self.search,
        )
        # endregion

        # ================================================
        # region   Chart frame
        # ================================================
        self.chart_frame = ttk.Frame(
            self,
            padding=10,
        )
        self.chart_frame.pack(
            fill=tk.BOTH,
            expand=True,
        )

        self.figure = plt.figure()

        self.chart = CHART_CLASS(self.figure)

        self.canvas = FigureCanvasTkAgg(
            self.figure,
            master=self.chart_frame,
        )

        self.canvas.get_tk_widget().pack(
            fill=tk.BOTH,
            expand=True,
        )
        # endregion

        # ================================================
        # region   Table frame
        # ================================================
        table_frame = ttk.Frame(
            self,
            padding=10,
        )
        table_frame.pack(
            fill=tk.BOTH
        )

        self.table = TABLE_CLASS(table_frame)
        self.table.pack(
            fill=tk.BOTH,
            expand=True,
        )
        # endregion

        # ================================================
        # region   Initial settings
        # ================================================
        try:
            machine_numbers = self.get_machine_numbers()

            self.machine_combo["values"] = machine_numbers

            if machine_numbers:
                self.machine_combo.current(0)

        except sqlite3.Error as error:
            messagebox.showerror(
                "Database Error",
                str(error),
            )

        today = datetime.now()


        first_day = today.replace(day=1).strftime("%Y-%m-%d")
        today = datetime.now().strftime("%Y-%m-%d")

        self.start_entry.insert(
            0,
            first_day,
        )

        self.end_entry.insert(
            0,
            today,
        )
        # endregion
        

    def get_machine_numbers(self) -> list[int]:
        """Get machine numbers from the database."""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT DISTINCT machine_no
            FROM alarm_history
            ORDER BY machine_no
            """
        )

        machine_numbers = [row[0] for row in cursor.fetchall()]

        conn.close()

        return machine_numbers

    def search(self, event=None) -> None:
        machine_no = self.machine_combo.get()
        start_date = self.start_entry.get().strip()
        end_date = self.end_entry.get().strip()

        if not machine_no or not start_date or not end_date:
            messagebox.showwarning(
                "Input Error",
                "Please enter all search conditions.",
            )
            return

        try:
            # Update chart
            self.chart.update(
                int(machine_no),
                start_date,
                end_date,
            )
            
            # Update table
            self.table.update(
                int(machine_no),
                start_date,
                end_date,
            )

        except sqlite3.Error as error:
            messagebox.showerror(
                "Database Error",
                str(error),
            )
            return

        self.canvas.draw()

    def change_date(self, entry: ttk.Entry, days: int) -> None:
        """Change the date by the specified number of days."""
        try:
            current_date = datetime.strptime(
                entry.get().strip(),
                "%Y-%m-%d",
            )

            new_date = current_date + timedelta(days=days)

            entry.delete(0, tk.END)
            entry.insert(
                0,
                new_date.strftime("%Y-%m-%d"),
            )

        except ValueError:
            return

    def change_month(self, entry: ttk.Entry, direction: int) -> None:
        """Change the month and set the day to 1."""
        try:
            current_date = datetime.strptime(
                entry.get().strip(),
                "%Y-%m-%d",
            )

            # Previous month
            if direction == -1:
                if current_date.day == 1:
                    new_date = current_date - timedelta(days=1)
                    new_date = new_date.replace(day=1)
                else:
                    new_date = current_date.replace(day=1)

            # Next month
            elif direction == 1:
                new_date = current_date.replace(day=1)
                new_date += timedelta(days=32)
                new_date = new_date.replace(day=1)

            else:
                return

            entry.delete(0, tk.END)
            entry.insert(0, new_date.strftime("%Y-%m-%d"))

        except ValueError:
            return
        

if __name__ == "__main__":
    root = tk.Tk()

    apply_style()

    root.title("Alarm Tab Test")
    root.geometry("1000x750")

    alarm_tab = AlarmTab(root)
    alarm_tab.pack(
        fill=tk.BOTH,
        expand=True,
    )

    def on_close() -> None:
        """Close matplotlib and destroy the Tkinter window."""
        plt.close(alarm_tab.figure)
        root.destroy()

    root.protocol(
        "WM_DELETE_WINDOW",
        on_close,
    )

    root.mainloop()


