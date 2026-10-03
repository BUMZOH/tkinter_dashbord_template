import sqlite3
import tkinter as tk
from pathlib import Path
from tkinter import ttk


# ================================================
#   Settings
# ================================================
BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "body_inspection_machine.db"

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


# ================================================
#   Alarm table
# ================================================
class AlarmTable(ttk.Frame):

    def __init__(self, parent):
        super().__init__(parent)

        self.tree = ttk.Treeview(
            self,
            columns=tuple(TABLE_COLUMNS.keys()),
            show="headings",
            height=10,
        )

        # Vertical scrollbar
        scrollbar = ttk.Scrollbar(
            self,
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
            expand=True,
        )

        scrollbar.pack(
            side=tk.RIGHT,
            fill=tk.Y,
        )

    def _get_alarm_history(
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

    def search(
        self,
        machine_no: int,
        start_date: str,
        end_date: str,
    ) -> None:
        """Search alarm history and update the table."""
        rows = self._get_alarm_history(
            machine_no,
            start_date,
            end_date,
        )

        self._update_table(rows)

    def _update_table(self, rows: list[tuple]) -> None:
        """Update table data."""
        for item in self.tree.get_children():
            self.tree.delete(item)

        for row in rows:
            self.tree.insert(
                "",
                tk.END,
                values=row,
            )


