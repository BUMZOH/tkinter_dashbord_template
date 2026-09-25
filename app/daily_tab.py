import sqlite3
import tkinter as tk
from datetime import datetime, timedelta
from pathlib import Path
from tkinter import messagebox, ttk

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

plt.rcParams["font.family"] = "Yu Gothic"
plt.rcParams["axes.unicode_minus"] = False

from style import apply_style


# ================================================
# region   Settings
# ================================================
BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "body_inspection_machine.db"


# Chart
# Change the chart type in the update_chart() method.
CHART_TITLE = "Daily Alarm Count"
CHART_X_LABEL = "Date"
CHART_Y_LABEL = "Count"
CHART_COLOR = "special"


# Table
TABLE_COLUMNS = {
    "datetime": {
        "text": "Datetime",
        "width": 200,
        "anchor": tk.CENTER,
    },
    "alarm_comment": {
        "text": "Alarm Comment",
        "width": 700,
        "anchor": tk.W,
    },
}
# endregion

class DailyTab(ttk.Frame):

    def __init__(self, parent):
        super().__init__(parent)

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

        self.search_button = ttk.Button(
            search_frame,
            text="Search",
            command=self.search,
        )
        self.search_button.pack(
            side=tk.LEFT,
            padx=20,
        )
        # endregion

        # ================================================
        # region   Chart frame
        # ================================================
        chart_frame = ttk.Frame(
            self,
            padding=10,
        )
        chart_frame.pack(
            fill=tk.BOTH,
            expand=True,
        )

        self.figure, self.ax = plt.subplots()

        self.canvas = FigureCanvasTkAgg(
            self.figure,
            master=chart_frame,
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

        self.tree = ttk.Treeview(
            table_frame,
            columns=tuple(TABLE_COLUMNS.keys()),
            show="headings",
            height=10
        )

        # Vertical scrollbar
        scrollbar = ttk.Scrollbar(
            table_frame,
            orient=tk.VERTICAL,
            command=self.tree.yview,
        )
        self.tree.configure(
            yscrollcommand=scrollbar.set,
        )

        for column_id, settings in TABLE_COLUMNS.items():
            self.tree.heading(
                column_id,
                text=settings["text"],
            )

            self.tree.column(
                column_id,
                width=settings["width"],
                anchor=settings["anchor"],
            )

        self.tree.pack(
            side=tk.LEFT,
            fill=tk.BOTH,
            expand=True
        )

        scrollbar.pack(
            side=tk.RIGHT,
            fill=tk.Y,
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
            # Data for chart
            chart_rows = self.get_daily_alarm_counts(
                int(machine_no),
                start_date,
                end_date,
            )

            # Data for table
            table_rows = self.get_alarm_history(
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

        self.update_chart(chart_rows)
        self.update_table(table_rows)

    def get_daily_alarm_counts(
        self,
        machine_no: int,
        start_date: str,
        end_date: str,
    ) -> list[tuple]:
        """Get daily alarm occurrence counts."""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT
                date(datetime) AS alarm_date,
                COUNT(*) AS alarm_count
            FROM alarm_history
            WHERE machine_no = ?
              AND datetime >= ?
              AND datetime < datetime(?, '+1 day')
            GROUP BY date(datetime)
            ORDER BY alarm_date
            """,
            (
                machine_no,
                start_date,
                end_date,
            ),
        )

        rows = cursor.fetchall()

        conn.close()

        return self.fill_missing_dates(
            rows,
            start_date,
            end_date,
        )    

    def fill_missing_dates(
        self,
        rows: list[tuple],
        start_date: str,
        end_date: str,
    ) -> list[tuple]:
        """Fill missing dates with zero."""
        count_by_date = dict(rows)
        
        result = []

        current_date = datetime.strptime(
            start_date,
            "%Y-%m-%d",
        )

        last_date = datetime.strptime(
            end_date,
            "%Y-%m-%d",
        )

        while current_date <= last_date:
            date_text = current_date.strftime("%Y-%m-%d")

            result.append(
                (
                    date_text,
                    count_by_date.get(date_text, 0),
                )
            )

            current_date += timedelta(days=1)

        return result

    def get_bar_colors(
        self,
        dates: list[str],
    ) -> str | list[str]:
        """Get bar colors."""
        if CHART_COLOR != "special":
            return CHART_COLOR

        colors = []

        for date_text in dates:
            date = datetime.strptime(
                date_text,
                "%Y-%m-%d",
            )

            if date.weekday() >= 5:
                colors.append("gray")
            else:
                colors.append("pink")

        return colors
            
    def get_alarm_history(
        self,
        machine_no: int,
        start_date: str,
        end_date: str,
    ) -> list[tuple]:
        """Get alarm history."""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT
                datetime,
                alarm_comment
            FROM alarm_history
            WHERE machine_no = ?
              AND datetime >= ?
              AND datetime < datetime(?, '+1 day')
            ORDER BY datetime ASC
            """,
            (
                machine_no,
                start_date,
                end_date,
            ),
        )

        rows = cursor.fetchall()

        conn.close()

        return rows

    def update_chart(self, rows: list[tuple]) -> None:
        self.ax.clear()

        if not rows:
            self.ax.set_title(CHART_TITLE)
            self.canvas.draw()
            return

        x_values = [row[0] for row in rows]
        y_values = [row[1] for row in rows]

        bar_colors = self.get_bar_colors(x_values)

        # Change as needed (e.g. bar, barh, plot, scatter).
        bars = self.ax.bar(
            x_values,
            y_values,
            color=bar_colors,
        )
        # Show values on the bars for bar() or barh().
        self.ax.bar_label(
            bars,
            padding=3,
        )

        self.ax.set_title(CHART_TITLE)
        self.ax.set_xlabel(CHART_X_LABEL)
        self.ax.set_ylabel(CHART_Y_LABEL)

        self.ax.tick_params(
            axis="x",
            labelrotation=90,
        )

        # Show total count at the bottom right.
        total_count = sum(row[1] for row in rows)

        self.ax.text(
            0.98,
            0.92,
            f"Total = {total_count}",
            transform=self.ax.transAxes,
            ha="right",
            va="bottom",
            fontsize=12,
            fontweight="bold",
        )

        self.figure.tight_layout()
        self.canvas.draw()

    def update_table(self, rows: list[tuple]) -> None:
        for item in self.tree.get_children():
            self.tree.delete(item)

        for row in rows:
            self.tree.insert(
                "",
                tk.END,
                values=row,
            )

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


if __name__ == "__main__":
    root = tk.Tk()

    apply_style()

    root.title("Daily Tab Test")
    root.geometry("1000x750")

    daily_tab = DailyTab(root)
    daily_tab.pack(
        fill=tk.BOTH,
        expand=True,
    )

    def on_close() -> None:
        """Close matplotlib and destroy the Tkinter window."""
        plt.close(daily_tab.figure)
        root.destroy()

    root.protocol(
        "WM_DELETE_WINDOW",
        on_close,
    )

    root.mainloop()






