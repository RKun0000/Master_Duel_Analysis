import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tools import load_font
# import mplcursors

from tools import center_window, resource_path


class OpponentDeckPieChart(tk.Toplevel):
    def __init__(self, app, records):
        super().__init__(app.root)
        self.title("本賽季對手卡組使用比例")
        self.geometry("850x850")
        self.records = records  # 傳入的是當前賽季的紀錄列表
        self.current_filter = "全部"  # 預設下拉選單選項
        load_font()
        self.create_widgets()
        self.update_chart()
        center_window(self, app.root)


    def create_widgets(self):
        # 上方區域：下拉選單與統計資訊
        top_frame = tk.Frame(self)
        top_frame.pack(fill=tk.X, padx=10, pady=5)
        tk.Label(top_frame, text="選擇段位:").pack(side=tk.LEFT)
        self.rank_filter_var = tk.StringVar(value="全部")
        self.rank_filter_option = ttk.Combobox(
            top_frame,
            textvariable=self.rank_filter_var,
            values=["全部", "競等賽", "Master", "Diamond", "Platinum", "Gold", "Silver"],
            state="readonly",
            width=10,
        )
        self.rank_filter_option.pack(side=tk.LEFT, padx=5)
        self.rank_filter_option.bind(
            "<<ComboboxSelected>>", lambda e: self.on_filter_change()
        )
        # 統計資訊 Label
        self.stats_label = tk.Label(top_frame, text="")
        self.stats_label.pack(side=tk.LEFT, padx=10)
        # 圖形區域
        self.canvas_frame = tk.Frame(self)
        self.canvas_frame.pack(fill=tk.BOTH, expand=True)

    def on_filter_change(self):
        self.current_filter = self.rank_filter_var.get()
        self.update_chart()

    def update_chart(self):
        # 篩選紀錄：若選擇 "全部"，則不篩選；否則檢查 record["rank"] 是否以選擇的段位開頭
        if self.current_filter == "全部":
            filtered = self.records
        else:
            filtered = [
                r
                for r in self.records
                if r.get("rank", "").startswith(self.current_filter)
            ]
        # 計算統計資訊
        total = len(filtered)
        wins = len([r for r in filtered if r.get("result") == "勝"])
        win_rate = (wins / total * 100) if total > 0 else 0
        self.stats_label.config(text=f"場數: {total} 勝率: {win_rate:.1f}%")
        # 計算對手卡組出現次數
        opp_deck_counts = {}
        for r in filtered:
            deck = r.get("opp_deck", "未知")
            opp_deck_counts[deck] = opp_deck_counts.get(deck, 0) + 1
        # 依數值由大到小排序
        sorted_items = sorted(
            opp_deck_counts.items(), key=lambda x: x[1], reverse=False
        )
        self.labels = [item[0] for item in sorted_items]
        self.sizes = [item[1] for item in sorted_items]
        # 清除先前的畫布（若有）
        if hasattr(self, "canvas"):
            self.canvas.get_tk_widget().destroy()
        # 建立圖形
        self.fig, self.ax = plt.subplots()
        self.wedges, self.texts, self.autotexts = self.ax.pie(
            self.sizes, labels=self.labels, autopct="%1.1f%%", startangle=90
        )
        self.ax.axis("equal")
        # 為每個 wedge 設定 picker 支援（可設定 5 像素容差）
        for w in self.wedges:
            w.set_picker(5)
        # 建立一個隱藏的註解，用於顯示游標提示資訊
        self.ann = self.ax.annotate(
            "",
            xy=(0, 0),
            xytext=(20, 20),
            textcoords="offset points",
            bbox=dict(boxstyle="round", fc="w"),
            arrowprops=dict(arrowstyle="->"),
        )
        self.ann.set_visible(False)
        self.fig.canvas.mpl_connect("motion_notify_event", self.on_move)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.canvas_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def on_move(self, event):
        if event.inaxes != self.ax:
            self.ann.set_visible(False)
            self.fig.canvas.draw_idle()
            return
        found = False
        # 遍歷每個 wedge，檢查滑鼠是否在其中
        for wedge, label, size in zip(self.wedges, self.labels, self.sizes):
            contains, _ = wedge.contains(event)
            if contains:
                self.ann.set_text(f"{label}: {size} 場")
                self.ann.xy = (event.xdata, event.ydata)
                self.ann.set_visible(True)
                found = True
                break
        if not found:
            self.ann.set_visible(False)
        self.fig.canvas.draw_idle()


class MyDeckPieChart(tk.Toplevel):
    def __init__(self, app, records):
        super().__init__(app.root)
        self.title("本賽季我方卡組使用比例")
        self.geometry("500x500")
        self.records = records
        load_font()
        self.create_chart()
        center_window(self, app.root)

    def create_chart(self):
        # 計算每個我方卡組的出場次數以及勝場數
        deck_counts = {}
        deck_wins = {}
        for rec in self.records:
            deck = rec.get("my_deck", "未知")
            deck_counts[deck] = deck_counts.get(deck, 0) + 1
            if rec.get("result") == "勝":
                deck_wins[deck] = deck_wins.get(deck, 0) + 1
            else:
                deck_wins.setdefault(deck, 0)
        # 儲存勝率資料供滑鼠提示使用
        self.deck_wins = deck_wins

        # 將結果依出場次數由大到小排序
        sorted_items = sorted(deck_counts.items(), key=lambda x: x[1], reverse=False)
        self.labels = [item[0] for item in sorted_items]
        self.sizes = [item[1] for item in sorted_items]

        total = sum(self.sizes)
        # 製作顯示於餅圖上的標籤：卡組名稱與百分比
        display_labels = [
            f"{label} ({(size/total*100):.1f}%)"
            for label, size in zip(self.labels, self.sizes)
        ]

        self.fig, self.ax = plt.subplots()
        # 繪製餅圖（不使用 autopct，因為我們自行設定標籤）
        self.wedges, self.texts = self.ax.pie(
            self.sizes, labels=display_labels, startangle=90
        )
        self.ax.axis("equal")

        # 建立一個隱藏的註解，用於顯示滑鼠提示資訊
        self.ann = self.ax.annotate(
            "",
            xy=(0, 0),
            xytext=(20, 20),
            textcoords="offset points",
            bbox=dict(boxstyle="round", fc="w"),
            arrowprops=dict(arrowstyle="->"),
        )
        self.ann.set_visible(False)

        self.fig.canvas.mpl_connect("motion_notify_event", self.on_move)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def on_move(self, event):
        if event.inaxes != self.ax:
            self.ann.set_visible(False)
            self.fig.canvas.draw_idle()
            return
        found = False
        # 遍歷每個 wedge，看滑鼠是否位於其中
        for wedge, label, size in zip(self.wedges, self.labels, self.sizes):
            contains, _ = wedge.contains(event)
            if contains:
                # 從 self.deck_wins 取出該卡組的勝場數
                wins = self.deck_wins.get(label, 0)
                total_games = size
                win_rate = (wins / total_games * 100) if total_games > 0 else 0
                self.ann.set_text(
                    f"{label}\n場次: {total_games}\n勝率: {win_rate:.1f}%"
                )
                self.ann.xy = (event.xdata, event.ydata)
                self.ann.set_visible(True)
                found = True
                break
        if not found:
            self.ann.set_visible(False)
        self.fig.canvas.draw_idle()
