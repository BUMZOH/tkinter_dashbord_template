import tkinter as tk
from tkinter import ttk

import matplotlib.pyplot as plt

from alarm_tab import AlarmTab
from daily_tab import DailyTab
from style import apply_style


# ================================================
#   Main window
# ================================================
root = tk.Tk()

apply_style()

root.title("Alarm History Viewer")
root.geometry("1000x750")

# ================================================
#   Notebook
# ================================================
notebook = ttk.Notebook(root)

notebook.pack(
    fill=tk.BOTH,
    expand=True,
)

# ================================================
#   Tab
# ================================================
alarm_tab = AlarmTab(notebook)
notebook.add(
    alarm_tab,
    text="アラーム別",
)

daily_tab = DailyTab(notebook)
notebook.add(
    daily_tab,
    text="日別",
)


# ================================================
#   Close
# ================================================
def on_close() -> None:
    """Close matplotlib and destroy the Tkinter window."""  
    plt.close(alarm_tab.figure)
    plt.close(daily_tab.figure)
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_close)


# ================================================
#   Start
# ================================================
root.mainloop()