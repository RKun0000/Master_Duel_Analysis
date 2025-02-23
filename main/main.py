import tkinter as tk
from ui import CardRecordApp

if __name__ == "__main__":
    root = tk.Tk()
    root.state("zoomed")  # 最大化視窗 (僅適用於 Windows)
    root.resizable(True, True)  # 允許使用者自行調整大小
    app = CardRecordApp(root)
    root.mainloop()
