import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib as mpl
import matplotlib.font_manager as fm
#import mplcursors

from tools import center_window, resource_path


class OpponentDeckPieChart(tk.Toplevel):
    def __init__(self, app, records):
        super().__init__(app.root)
        self.title("本賽季對手卡組使用比例")
        self.geometry("850x850")
        self.records = records  # 傳入的是當前賽季的紀錄列表
        self.current_filter = "全部"  # 預設下拉選單選項
        self.load_font()
        self.create_widgets()
        self.update_chart()
        center_window(self, app.root)

    def load_font(self):
            # 加入自訂字體
        font_path = resource_path("TaipeiSansTCBeta-Regular.ttf")
        fm.fontManager.addfont(font_path)
        custom_font = fm.FontProperties(fname=font_path).get_name()

        # 設定全域字體為自訂字體
        mpl.rcParams["font.sans-serif"] = [custom_font]
        mpl.rcParams["font.family"] = "sans-serif"
        mpl.rcParams["axes.unicode_minus"] = False  # 避免負號顯示問題

    def create_widgets(self):
        # 上方區域：下拉選單與統計資訊
        top_frame = tk.Frame(self)
        top_frame.pack(fill=tk.X, padx=10, pady=5)
        tk.Label(top_frame, text="選擇段位:").pack(side=tk.LEFT)
        self.rank_filter_var = tk.StringVar(value="全部")
        self.rank_filter_option = ttk.Combobox(
            top_frame,
            textvariable=self.rank_filter_var,
            values=["全部", "白金", "鑽石", "大師", "競等賽"],
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
