import sqlite3
from pathlib import Path

from matplotlib.figure import Figure


# ================================================
#   Settings
# ================================================
BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "body_inspection_machine.db"

CHART_TITLE = "Alarm Occurrence Count"
CHART_X_LABEL = "Count"
CHART_Y_LABEL = ""
CHART_COLOR = "pink"


# ================================================
#   Create chart
# ================================================
def create_alarm_chart(
        figure: Figure,
        machine_no: int,
        start_date: str,
        end_date: str,
) -> None:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT 
            alarm_comment,
            COUNT(*) AS alarm_count
        FROM alarm_history
        WHERE machine_no = ?
          AND datetime >= ?
          AND datetime < datetime(?, '+1 day')
        GROUP BY alarm_comment
        ORDER BY alarm_count DESC
        """,
        (
            machine_no,
            start_date,
            end_date,
        ),
    )

    rows = cursor.fetchall()

    conn.close()

    figure.clear()

    # Add a single subplot (1 row, 1 column, position 1).
    ax = figure.add_subplot(111)

    if not rows:
        ax.set_title(CHART_TITLE)
        return

    x_values = [row[0] for row in rows]
    y_values = [row[1] for row in rows]

    # Reverse the order so that the largest value appears at the top.
    x_values.reverse()
    y_values.reverse()

    bars = ax.barh(
        x_values,
        y_values,
        color=CHART_COLOR,
    )

    ax.bar_label(
        bars,
        padding=3,
    )

    ax.set_title(CHART_TITLE)
    ax.set_xlabel(CHART_X_LABEL)
    ax.set_ylabel(CHART_Y_LABEL)

    # Show total count at the bottom right.
    total_count = sum(row[1] for row in rows)

    ax.text(
        0.98,
        0.02,
        f"Total = {total_count}",
        transform=ax.transAxes,
        ha="right",
        va="bottom",
        fontsize=12,
        fontweight="bold",
    )

    figure.tight_layout()





