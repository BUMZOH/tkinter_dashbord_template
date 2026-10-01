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
#   Navigation frame
# ================================================
nav_frame = ttk.Frame(
    root,
    width=160,
    # borderwidth=1,
    # relief="solid",
    style="Nav.TFrame",
    padding=10,
)

nav_frame.pack(
    side=tk.LEFT,
    fill=tk.Y,
)

nav_frame.pack_propagate(False)


# ================================================
#   Main frame
# ================================================
main_frame = ttk.Frame(
    root,
    # borderwidth=1,
    # relief="solid",
)

main_frame.pack(
    side=tk.LEFT,
    fill=tk.BOTH,
    expand=True,
)


# ================================================
#   Pages
# ================================================
page1 = AlarmTab(main_frame)
page2 = DailyTab(main_frame)

page1.place(x=0, y=0, relwidth=1, relheight=1)
page2.place(x=0, y=0, relwidth=1, relheight=1)


# ================================================
#   Page switching
# ================================================
def show_page(page):
    page.tkraise()


# ================================================
#   Navigation title
# ================================================
ttk.Label(
    nav_frame,
    text="MENU",
    style="NavTitle.TLabel",
).pack(
    padx=10,
    pady=(30, 5),
)


# ================================================
#   Navigation buttons
# ================================================
nav_button1 = ttk.Button(
    nav_frame,
    text="アラーム別",
    command=lambda: show_page(page1),
)

nav_button1.pack(
    fill=tk.X,
    padx=10,
    pady=(10, 5),
)

nav_button2 = ttk.Button(
    nav_frame,
    text="日別",
    command=lambda: show_page(page2),
)

nav_button2.pack(
    fill=tk.X,
    padx=10,
    pady=5,
)

show_page(page1)


# ================================================
#   Version
# ================================================
version_label = ttk.Label(
    nav_frame,
    text="Ver.20261001-1",
    style="Version.TLabel",
)

version_label.pack(
    side=tk.BOTTOM,
    pady=10,
)


# ================================================
#   Close
# ================================================
def on_close() -> None:
    """Close matplotlib and destroy the Tkinter window."""  
    plt.close(page1.figure)
    plt.close(page2.figure)
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_close)


# ================================================
#   Start
# ================================================
root.mainloop()