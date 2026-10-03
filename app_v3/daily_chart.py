import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

from matplotlib.figure import Figure


# ================================================
#   Settings
# ================================================
BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "body_inspection_machine.db"

CHART_TITLE = "Daily Alarm Count"
CHART_X_LABEL = "Date"
CHART_Y_LABEL = "Count"
CHART_COLOR = "special"


# ================================================
#   Create chart
# ================================================
class DailyChart:
    def __init__(self, figure: Figure):
        self.figure = figure

    def update(
            self,
            machine_no: int,
            start_date: str,
            end_date: str,
    ) -> None:
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

        rows = self.fill_missing_dates(
            rows,
            start_date,
            end_date,
        )

        self.figure.clear()

        # Add a single subplot (1 row, 1 column, position 1).
        ax = self.figure.add_subplot(111)

        if not rows:
            ax.set_title(CHART_TITLE)
            return

        x_values = [row[0] for row in rows]
        y_values = [row[1] for row in rows]

        bar_colors = self.get_bar_colors(x_values)

        bars = ax.bar(
            x_values,
            y_values,
            color=bar_colors,
        )

        ax.bar_label(
            bars,
            padding=3,
        )

        ax.set_title(CHART_TITLE)
        ax.set_xlabel(CHART_X_LABEL)
        ax.set_ylabel(CHART_Y_LABEL)

        ax.tick_params(
            axis="x",
            labelrotation=90,
        )

        # Show total count at the top right.
        total_count = sum(row[1] for row in rows)

        ax.text(
            0.98,
            0.92,
            f"Total = {total_count}",
            transform=ax.transAxes,
            ha="right",
            va="bottom",
            fontsize=12,
            fontweight="bold",
        )

        self.figure.tight_layout()

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


if __name__ == "__main__":
    import matplotlib.pyplot as plt
    plt.rcParams["font.family"] = "Yu Gothic"

    figure = plt.figure()

    chart = DailyChart(figure)

    chart.update(
        machine_no=412,
        start_date="2026-09-01",
        end_date="2026-09-30",
    )

    plt.show()


