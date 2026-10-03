"""
Tkinter command + lambda の注意点

forループ内で `lambda: show_page(page)` とすると、
lambdaは実行時に page を参照するため、最後の page が使われる。
これは Python の遅延束縛（late binding）によるもの。

`lambda p=page: show_page(p)` とすることで、
デフォルト引数 p に lambda 作成時点の page の値を保存できる。
つまり、デフォルト引数を利用して現在の値をキャプチャしている。
Tkinterでループから複数のButtonを作成するときに重要なテクニック。
"""
import tkinter as tk
from tkinter import ttk


root =tk.Tk()
root.geometry("300x200")


pages = [
    "AlarmTab",
    "DailyTab",
]


def show_page(page):
    print(page)


for page in pages:
    button = ttk.Button(
        root,
        text=page,
        command=lambda p=page: show_page(p),
    )
    button.pack(padx=20, pady=10)

root.mainloop()



