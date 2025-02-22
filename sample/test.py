import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import json
import os
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib as mpl
import matplotlib.font_manager as fm
import mplcursors

# 加入自訂字體
font_path = "TaipeiSansTCBeta-Regular.ttf"
fm.fontManager.addfont(font_path)
custom_font = fm.FontProperties(fname=font_path).get_name()

# 設定全域字體為自訂字體
mpl.rcParams["font.sans-serif"] = [custom_font]
mpl.rcParams["font.family"] = "sans-serif"
mpl.rcParams["axes.unicode_minus"] = False  # 避免負號顯示問題


# ---------------------------
# 卡組管理視窗
# ---------------------------
class DeckManagementWindow(tk.Toplevel):
    def __init__(self, master, deck_list, deck_type, update_callback):
        super().__init__(master)
        self.title(f"{deck_type}管理")
        self.deck_list = deck_list
        self.deck_type = deck_type
        self.update_callback = update_callback
        self.geometry("400x300")
        self.create_widgets()

    def create_widgets(self):
        self.listbox = tk.Listbox(self)
        self.listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        for deck in self.deck_list:
            self.listbox.insert(tk.END, deck)
        self.entry = tk.Entry(self)
        self.entry.pack(fill=tk.X, padx=10, pady=5)
        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=5)
        btn_add = tk.Button(btn_frame, text="新增", command=self.add_deck)
        btn_add.pack(side=tk.LEFT, padx=5)
        btn_modify = tk.Button(btn_frame, text="修改", command=self.modify_deck)
        btn_modify.pack(side=tk.LEFT, padx=5)
        btn_delete = tk.Button(btn_frame, text="刪除", command=self.delete_deck)
        btn_delete.pack(side=tk.LEFT, padx=5)
        btn_close = tk.Button(btn_frame, text="關閉", command=self.destroy)
        btn_close.pack(side=tk.LEFT, padx=5)

    def add_deck(self):
        new_deck = self.entry.get().strip()
        if new_deck == "":
            messagebox.showinfo("提示", "卡組名稱不能為空!")
            return
        if new_deck in self.deck_list:
            messagebox.showinfo("提示", "該卡組已存在!")
            return
        self.deck_list.append(new_deck)
        self.listbox.insert(tk.END, new_deck)
        self.entry.delete(0, tk.END)
        self.update_callback()

    def modify_deck(self):
        selection = self.listbox.curselection()
        if not selection:
            messagebox.showinfo("提示", "請選擇要修改的卡組!")
            return
        index = selection[0]
        new_name = self.entry.get().strip()
        if new_name == "":
            messagebox.showinfo("提示", "卡組名稱不能為空!")
            return
        if new_name in self.deck_list:
            messagebox.showinfo("提示", "該卡組已存在!")
            return
        self.deck_list[index] = new_name
        self.listbox.delete(index)
        self.listbox.insert(index, new_name)
        self.entry.delete(0, tk.END)
        self.update_callback()

    def delete_deck(self):
        selection = self.listbox.curselection()
        if not selection:
            messagebox.showinfo("提示", "請選擇要刪除的卡組!")
            return
        index = selection[0]
        if not self.deck_list or index >= len(self.deck_list):
            messagebox.showinfo("提示", "卡組列表中沒有該項目!")
            return
        self.deck_list.pop(index)
        self.listbox.delete(index)
        self.update_callback()


# ---------------------------
# 賽季管理視窗
# ---------------------------
class SeasonManagementWindow(tk.Toplevel):
    def __init__(self, app):
        super().__init__(app.root)
        self.app = app
        self.title("賽季管理")
        self.geometry("300x350")
        self.create_widgets()

    def create_widgets(self):
        tk.Label(self, text="現有賽季:").pack(pady=5)
        self.season_listbox = tk.Listbox(self)
        self.season_listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        self.refresh_season_list()

        # 新增賽季輸入區
        add_frame = tk.Frame(self)
        add_frame.pack(pady=5)
        tk.Label(add_frame, text="新增賽季:").pack(side=tk.LEFT)
        self.new_season_entry = tk.Entry(add_frame, width=10)
        self.new_season_entry.pack(side=tk.LEFT, padx=5)
        btn_add = tk.Button(add_frame, text="建立新賽季", command=self.add_season)
        btn_add.pack(side=tk.LEFT, padx=5)

        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=5)
        btn_load = tk.Button(btn_frame, text="載入賽季", command=self.load_season)
        btn_load.pack(side=tk.LEFT, padx=5)
        btn_delete = tk.Button(
            btn_frame, text="刪除賽季資料", command=self.delete_season
        )
        btn_delete.pack(side=tk.LEFT, padx=5)
        btn_close = tk.Button(btn_frame, text="關閉", command=self.destroy)
        btn_close.pack(side=tk.LEFT, padx=5)

    def refresh_season_list(self):
        seasons = set()
        for rec in self.app.records:
            seasons.add(rec.get("season", self.app.current_season))
        seasons.add(self.app.current_season)
        seasons = sorted(list(seasons))
        self.season_listbox.delete(0, tk.END)
        for s in seasons:
            self.season_listbox.insert(tk.END, s)

    def add_season(self):
        new_season = self.new_season_entry.get().strip()
        if new_season == "":
            messagebox.showinfo("提示", "請輸入賽季代號")
            return
        # 檢查是否已存在
        seasons = set(
            r.get("season", self.app.current_season) for r in self.app.records
        )
        seasons.add(self.app.current_season)
        if new_season in seasons:
            messagebox.showinfo("提示", "該賽季已存在")
            return
        # 新增新賽季（此處僅更改當前賽季，新賽季的資料尚無）
        self.app.current_season = new_season
        self.app.season_label.config(text=new_season)
        self.new_season_entry.delete(0, tk.END)
        self.refresh_season_list()
        self.app.refresh_tree_records()  # 切換到新賽季，記錄列表將顯示該賽季資料
        messagebox.showinfo("提示", f"已建立並載入賽季 {new_season}")

    def load_season(self):
        selection = self.season_listbox.curselection()
        if not selection:
            messagebox.showinfo("提示", "請選擇要載入的賽季!")
            return
        season = self.season_listbox.get(selection[0])
        self.app.current_season = season
        self.app.season_label.config(text=season)
        self.app.refresh_tree_records()
        messagebox.showinfo("提示", f"已載入賽季 {season}")

    def delete_season(self):
        selection = self.season_listbox.curselection()
        if not selection:
            messagebox.showinfo("提示", "請選擇要刪除的賽季!")
            return
        season = self.season_listbox.get(selection[0])
        if season == self.app.current_season:
            messagebox.showwarning("警告", "不能刪除目前載入的賽季!")
            return
        if messagebox.askyesno("確認", f"確定要刪除賽季 {season} 的所有資料嗎？"):
            self.app.records = [
                r for r in self.app.records if r.get("season") != season
            ]
            self.app.refresh_tree_records()
            self.refresh_season_list()
            messagebox.showinfo("提示", f"已刪除賽季 {season} 的資料")


# ---------------------------
# 修改紀錄視窗
# ---------------------------
class RecordModifyWindow(tk.Toplevel):
    def __init__(self, app, record):
        super().__init__(app.root)
        self.app = app
        self.record = record
        self.title("修改紀錄")
        self.geometry("400x450")
        self.create_widgets()

    def create_widgets(self):
        tk.Label(self, text="我方卡組:").grid(
            row=0, column=0, padx=5, pady=5, sticky="e"
        )
        self.my_deck_var_mod = tk.StringVar(value=self.record["my_deck"])
        self.my_deck_option_mod = ttk.Combobox(
            self,
            textvariable=self.my_deck_var_mod,
            values=self.app.my_decks,
            state="readonly",
            width=15,
        )
        self.my_deck_option_mod.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(self, text="對方卡組:").grid(
            row=1, column=0, padx=5, pady=5, sticky="e"
        )
        self.opp_deck_var_mod = tk.StringVar(value=self.record["opp_deck"])
        self.opp_deck_option_mod = ttk.Combobox(
            self,
            textvariable=self.opp_deck_var_mod,
            values=self.app.opp_decks,
            state="readonly",
            width=15,
        )
        self.opp_deck_option_mod.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(self, text="勝負:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.result_var_mod = tk.StringVar(value=self.record["result"])
        self.result_option_mod = ttk.Combobox(
            self,
            textvariable=self.result_var_mod,
            values=["勝", "敗"],
            state="readonly",
            width=15,
        )
        self.result_option_mod.grid(row=2, column=1, padx=5, pady=5)

        tk.Label(self, text="先後手:").grid(row=3, column=0, padx=5, pady=5, sticky="e")
        self.turn_var_mod = tk.StringVar(value=self.record["turn"])
        self.turn_option_mod = ttk.Combobox(
            self,
            textvariable=self.turn_var_mod,
            values=["先手", "後手"],
            state="readonly",
            width=15,
        )
        self.turn_option_mod.grid(row=3, column=1, padx=5, pady=5)

        tk.Label(self, text="硬幣:").grid(row=4, column=0, padx=5, pady=5, sticky="e")
        self.coin_var_mod = tk.StringVar(value=self.record.get("coin", "正面"))
        self.coin_option_mod = ttk.Combobox(
            self,
            textvariable=self.coin_var_mod,
            values=["正面", "反面"],
            state="readonly",
            width=15,
        )
        self.coin_option_mod.grid(row=4, column=1, padx=5, pady=5)

        tk.Label(self, text="段位:").grid(row=5, column=0, padx=5, pady=5, sticky="e")
        self.rank_var_mod = tk.StringVar(value=self.record.get("rank", "白金1"))
        rank_options = [
            "白金1",
            "白金2",
            "白金3",
            "白金4",
            "白金5",
            "鑽石1",
            "鑽石2",
            "鑽石3",
            "鑽石4",
            "鑽石5",
            "大師1",
            "大師2",
            "大師3",
            "大師4",
            "大師5",
            "競等賽",
        ]
        self.rank_option_mod = ttk.Combobox(
            self,
            textvariable=self.rank_var_mod,
            values=rank_options,
            state="readonly",
            width=15,
        )
        self.rank_option_mod.grid(row=5, column=1, padx=5, pady=5)

        # 將「先攻是否中G」與「展開是否中G以外手坑」分別獨立上下排列
        tk.Label(self, text="先攻是否中G:").grid(
            row=6, column=0, padx=5, pady=5, sticky="e"
        )
        self.firstG_var_mod = tk.BooleanVar(value=(self.record["firstG"] == "是"))
        self.firstG_cb_mod = tk.Checkbutton(self, variable=self.firstG_var_mod)
        self.firstG_cb_mod.grid(row=6, column=1, padx=5, pady=5, sticky="w")

        tk.Label(self, text="展開是否中G以外手坑:").grid(
            row=7, column=0, padx=5, pady=5, sticky="e"
        )
        self.expanded_var_mod = tk.BooleanVar(
            value=(self.record.get("expanded", "否") == "是")
        )
        self.expanded_cb_mod = tk.Checkbutton(self, variable=self.expanded_var_mod)
        self.expanded_cb_mod.grid(row=7, column=1, padx=5, pady=5, sticky="w")

        # 自動計算「是否被讓先」：不供使用者修改
        computed_forced = (
            "是"
            if (
                self.record.get("coin", "正面") == "反面"
                and self.record["turn"] == "先手"
            )
            else "否"
        )
        tk.Label(self, text="是否被讓先:").grid(
            row=8, column=0, padx=5, pady=5, sticky="e"
        )
        self.forced_first_label_mod = tk.Label(self, text=computed_forced)
        self.forced_first_label_mod.grid(row=8, column=1, padx=5, pady=5, sticky="w")

        tk.Label(self, text="備註:").grid(row=9, column=0, padx=5, pady=5, sticky="e")
        self.note_entry_mod = tk.Entry(self, width=30)
        self.note_entry_mod.insert(0, self.record["note"])
        self.note_entry_mod.grid(row=9, column=1, padx=5, pady=5)

        btn_save = tk.Button(self, text="確認修改", command=self.save_changes)
        btn_save.grid(row=10, column=0, columnspan=2, pady=10)

    def save_changes(self):
        self.record["my_deck"] = self.my_deck_var_mod.get()
        self.record["opp_deck"] = self.opp_deck_var_mod.get()
        self.record["result"] = self.result_var_mod.get()
        self.record["turn"] = self.turn_var_mod.get()
        self.record["coin"] = self.coin_var_mod.get()
        self.record["rank"] = self.rank_var_mod.get()
        self.record["forced_first"] = (
            "是"
            if (self.record["coin"] == "反面" and self.record["turn"] == "先手")
            else "否"
        )
        self.record["firstG"] = "是" if self.firstG_var_mod.get() else "否"
        self.record["expanded"] = "是" if self.expanded_var_mod.get() else "否"
        self.record["note"] = self.note_entry_mod.get()
        self.app.tree.item(
            str(self.record["id"]),
            values=(
                self.record["my_deck"],
                self.record["opp_deck"],
                self.record["result"],
                self.record["turn"],
                self.record["rank"],
                self.record["coin"],
                self.record["forced_first"],
                self.record["firstG"],
                self.record["expanded"],
                self.record["note"],
                self.record.get("season", self.app.current_season),
            ),
        )
        self.app.update_statistics()
        self.destroy()


# ---------------------------
# 新增對手卡組使用比例圖視窗
# ---------------------------
# import mplcursors  # 在檔案開頭引入


class OpponentDeckPieChart(tk.Toplevel):
    def __init__(self, app, records):
        super().__init__(app.root)
        self.title("本賽季對手卡組使用比例")
        self.geometry("600x600")
        self.records = records
        # 下拉式選單選擇段位
        top_frame = tk.Frame(self)
        top_frame.pack(pady=5)
        tk.Label(top_frame, text="選擇段位:").pack(side=tk.LEFT)
        self.rank_filter_var = tk.StringVar(value="全部")
        rank_options = ["全部", "白金", "鑽石", "大師", "競等賽"]
        self.rank_filter_option = ttk.Combobox(
            top_frame,
            textvariable=self.rank_filter_var,
            values=rank_options,
            state="readonly",
            width=10,
        )
        self.rank_filter_option.pack(side=tk.LEFT, padx=5)
        self.rank_filter_option.bind(
            "<<ComboboxSelected>>", lambda e: self.update_chart()
        )
        # 用來顯示選定段位的場數與勝率
        self.info_label = tk.Label(self, text="")
        self.info_label.pack(pady=5)
        # 建立圖形區域
        self.fig, self.ax = plt.subplots()
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        self.update_chart()

    def update_chart(self):
        # 過濾當前賽季紀錄中，依據下拉式選單所選段位
        rank_filter = self.rank_filter_var.get()
        # self.records 為傳入的當前賽季紀錄
        filtered = self.records
        if rank_filter != "全部":
            filtered = [
                r for r in self.records if r.get("rank", "").startswith(rank_filter)
            ]
        # 統計對手卡組次數
        opp_deck_counts = {}
        for r in filtered:
            deck = r.get("opp_deck", "未知")
            opp_deck_counts[deck] = opp_deck_counts.get(deck, 0) + 1
        sorted_items = sorted(opp_deck_counts.items(), key=lambda x: x[1], reverse=True)
        labels = [item[0] for item in sorted_items]
        sizes = [item[1] for item in sorted_items]
        self.ax.clear()
        if sizes:
            wedges, texts, autotexts = self.ax.pie(
                sizes, labels=labels, autopct="%1.1f%%", startangle=90
            )
            self.ax.axis("equal")
        else:
            self.ax.text(
                0.5,
                0.5,
                "無資料",
                horizontalalignment="center",
                verticalalignment="center",
            )
        self.canvas.draw()
        # 計算該段位的場數與勝率
        total_matches = len(filtered)
        if total_matches > 0:
            wins = len([r for r in filtered if r.get("result") == "勝"])
            win_rate = wins / total_matches * 100
            info_text = f"{rank_filter} 總場數: {total_matches}, 勝率: {win_rate:.1f}%"
        else:
            info_text = f"{rank_filter} 無資料"
        self.info_label.config(text=info_text)


# ---------------------------
# 賽季管理視窗
# ---------------------------
class SeasonManagementWindow(tk.Toplevel):
    def __init__(self, app):
        super().__init__(app.root)
        self.app = app
        self.title("賽季管理")
        self.geometry("300x300")
        self.create_widgets()

    def create_widgets(self):
        tk.Label(self, text="選擇賽季:").pack(pady=5)
        self.season_listbox = tk.Listbox(self)
        self.season_listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        self.refresh_season_list()
        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=5)
        btn_load = tk.Button(btn_frame, text="載入賽季", command=self.load_season)
        btn_load.pack(side=tk.LEFT, padx=5)
        btn_delete = tk.Button(
            btn_frame, text="刪除賽季資料", command=self.delete_season
        )
        btn_delete.pack(side=tk.LEFT, padx=5)
        btn_close = tk.Button(btn_frame, text="關閉", command=self.destroy)
        btn_close.pack(side=tk.LEFT, padx=5)

    def refresh_season_list(self):
        seasons = set()
        for rec in self.app.records:
            seasons.add(rec.get("season", self.app.current_season))
        seasons.add(self.app.current_season)
        seasons = sorted(list(seasons))
        self.season_listbox.delete(0, tk.END)
        for s in seasons:
            self.season_listbox.insert(tk.END, s)

    def load_season(self):
        selection = self.season_listbox.curselection()
        if not selection:
            messagebox.showinfo("提示", "請選擇要載入的賽季!")
            return
        season = self.season_listbox.get(selection[0])
        self.app.current_season = season
        self.app.season_label.config(text=season)
        self.app.refresh_tree_records()
        messagebox.showinfo("提示", f"已載入賽季 {season}")

    def delete_season(self):
        selection = self.season_listbox.curselection()
        if not selection:
            messagebox.showinfo("提示", "請選擇要刪除的賽季!")
            return
        season = self.season_listbox.get(selection[0])
        if season == self.app.current_season:
            messagebox.showwarning("警告", "不能刪除目前載入的賽季!")
            return
        if messagebox.askyesno("確認", f"確定要刪除賽季 {season} 的所有資料嗎？"):
            self.app.records = [
                r for r in self.app.records if r.get("season") != season
            ]
            self.app.refresh_tree_records()
            self.refresh_season_list()
            messagebox.showinfo("提示", f"已刪除賽季 {season} 的資料")


# ---------------------------
# 主應用程式
# ---------------------------
class CardRecordApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Master Duel Analysis")
        self.root.geometry("1200x850")
        self.root.resizable(False, False)
        self.my_decks = []
        self.opp_decks = []
        self.records = []
        self.record_id_counter = 0
        self.current_season = "S38"  # 預設賽季
        self.stats_deck_var = tk.StringVar()
        self.filter_var = tk.StringVar(value="全部")
        self.load_data()
        self.create_top_menu()
        self.create_main_area()
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def create_top_menu(self):
        top_frame = tk.Frame(self.root)
        top_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)
        btn_my_deck = tk.Button(
            top_frame, text="我方卡組管理", command=self.manage_my_decks
        )
        btn_my_deck.pack(side=tk.LEFT, padx=5)
        btn_opp_deck = tk.Button(
            top_frame, text="對方卡組管理", command=self.manage_opp_decks
        )
        btn_opp_deck.pack(side=tk.LEFT, padx=5)
        btn_season = tk.Button(
            top_frame, text="賽季管理", command=lambda: SeasonManagementWindow(self)
        )
        btn_season.pack(side=tk.LEFT, padx=5)

    def create_main_area(self):
        # 使用 grid 分左右兩個區域
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=0)

        # 左側區域：輸入表單
        left_frame = tk.Frame(main_frame)
        left_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        self.create_record_form(left_frame)

        # 右側區域：統計數據區，先建立統計面板
        right_frame = tk.Frame(main_frame, width=300)
        right_frame.grid(row=0, column=1, sticky="n", padx=(10, 0))
        right_frame.grid_propagate(False)
        self.create_statistics_panel(right_frame)

        # 最後建立戰績列表，此處 load_tree_records 會呼叫 update_statistics，
        # 此時統計元件已經存在，就不會再出現錯誤。
        self.create_record_list(left_frame)

    def create_record_form(self, parent):
        form_frame = tk.LabelFrame(parent, text="新增戰績紀錄")
        form_frame.pack(fill=tk.X, padx=5, pady=5)
        tk.Label(form_frame, text="我方卡組:").grid(
            row=0, column=0, padx=5, pady=5, sticky="e"
        )
        self.my_deck_var_form = tk.StringVar()
        self.my_deck_option = ttk.Combobox(
            form_frame,
            textvariable=self.my_deck_var_form,
            values=self.my_decks,
            state="readonly",
            width=15,
        )
        self.my_deck_option.grid(row=0, column=1, padx=5, pady=5)
        tk.Label(form_frame, text="對方卡組:").grid(
            row=0, column=2, padx=5, pady=5, sticky="e"
        )
        self.opp_deck_var_form = tk.StringVar()
        self.opp_deck_option = ttk.Combobox(
            form_frame,
            textvariable=self.opp_deck_var_form,
            values=self.opp_decks,
            state="readonly",
            width=15,
        )
        self.opp_deck_option.grid(row=0, column=3, padx=5, pady=5)
        tk.Label(form_frame, text="勝負:").grid(
            row=1, column=0, padx=5, pady=5, sticky="e"
        )
        self.result_var = tk.StringVar(value="勝")
        self.result_option = ttk.Combobox(
            form_frame,
            textvariable=self.result_var,
            values=["勝", "敗"],
            state="readonly",
            width=15,
        )
        self.result_option.grid(row=1, column=1, padx=5, pady=5)
        tk.Label(form_frame, text="先後手:").grid(
            row=1, column=2, padx=5, pady=5, sticky="e"
        )
        self.turn_var = tk.StringVar(value="先手")
        self.turn_option = ttk.Combobox(
            form_frame,
            textvariable=self.turn_var,
            values=["先手", "後手"],
            state="readonly",
            width=15,
        )
        self.turn_option.grid(row=1, column=3, padx=5, pady=5)
        tk.Label(form_frame, text="先攻是否中G:").grid(
            row=2, column=0, padx=5, pady=5, sticky="e"
        )
        self.firstG_var = tk.BooleanVar()
        self.firstG_cb = tk.Checkbutton(form_frame, variable=self.firstG_var)
        self.firstG_cb.grid(row=2, column=1, padx=5, pady=5, sticky="w")
        tk.Label(form_frame, text="展開是否中G以外手坑:").grid(
            row=2, column=2, padx=5, pady=5, sticky="e"
        )
        self.expanded_var = tk.BooleanVar()
        self.expanded_cb = tk.Checkbutton(form_frame, variable=self.expanded_var)
        self.expanded_cb.grid(row=2, column=3, padx=5, pady=5, sticky="w")
        tk.Label(form_frame, text="硬幣:").grid(
            row=3, column=0, padx=5, pady=5, sticky="e"
        )
        self.coin_var = tk.StringVar(value="正面")
        self.coin_option = ttk.Combobox(
            form_frame,
            textvariable=self.coin_var,
            values=["正面", "反面"],
            state="readonly",
            width=15,
        )
        self.coin_option.grid(row=3, column=1, padx=5, pady=5)
        tk.Label(form_frame, text="段位:").grid(
            row=4, column=0, padx=5, pady=5, sticky="e"
        )
        self.rank_var = tk.StringVar(value="白金1")
        rank_options = [
            "白金1",
            "白金2",
            "白金3",
            "白金4",
            "白金5",
            "鑽石1",
            "鑽石2",
            "鑽石3",
            "鑽石4",
            "鑽石5",
            "大師1",
            "大師2",
            "大師3",
            "大師4",
            "大師5",
            "競等賽",
        ]
        self.rank_option = ttk.Combobox(
            form_frame,
            textvariable=self.rank_var,
            values=rank_options,
            state="readonly",
            width=15,
        )
        self.rank_option.grid(row=4, column=1, padx=5, pady=5)
        tk.Label(form_frame, text="備註:").grid(
            row=5, column=0, padx=5, pady=5, sticky="e"
        )
        self.note_entry = tk.Entry(form_frame, width=50)
        self.note_entry.grid(row=5, column=1, columnspan=3, padx=5, pady=5, sticky="w")
        submit_btn = tk.Button(form_frame, text="新增紀錄", command=self.add_record)
        submit_btn.grid(row=6, column=0, columnspan=4, pady=10)

    def create_record_list(self, parent):
        list_frame = tk.LabelFrame(parent, text="戰績紀錄列表")
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        top_list_frame = tk.Frame(list_frame)
        top_list_frame.pack(fill=tk.X, padx=5, pady=5)
        tk.Label(top_list_frame, text="賽季:").pack(side=tk.LEFT)
        self.season_label = tk.Label(top_list_frame, text=self.current_season)
        self.season_label.pack(side=tk.LEFT, padx=5)
        tk.Label(top_list_frame, text="篩選(我方卡組):").pack(side=tk.LEFT, padx=10)
        self.filter_var.set("全部")
        filter_options = ["全部"] + self.my_decks
        self.filter_option = ttk.Combobox(
            top_list_frame,
            textvariable=self.filter_var,
            values=filter_options,
            state="readonly",
            width=15,
        )
        self.filter_option.pack(side=tk.LEFT, padx=5)
        self.filter_option.bind("<<ComboboxSelected>>", lambda e: self.filter_records())
        columns = (
            "my_deck",
            "opp_deck",
            "result",
            "turn",
            "rank",
            "coin",
            "forced_first",
            "firstG",
            "expanded",
            "note",
            "season",
        )
        self.tree = ttk.Treeview(
            list_frame, columns=columns, show="headings", selectmode="browse", height=15
        )
        self.tree.heading("my_deck", text="我方卡組", anchor="center")
        self.tree.heading("opp_deck", text="對方卡組", anchor="center")
        self.tree.heading("result", text="勝負", anchor="center")
        self.tree.heading("turn", text="先後手", anchor="center")
        self.tree.heading("rank", text="段位", anchor="center")
        self.tree.heading("coin", text="硬幣", anchor="center")
        self.tree.heading("forced_first", text="是否被讓先", anchor="center")
        self.tree.heading("firstG", text="先攻是否中G", anchor="center")
        self.tree.heading("expanded", text="展開是否中G以外手坑", anchor="center")
        self.tree.heading("note", text="備註", anchor="center")
        self.tree.heading("season", text="賽季", anchor="center")
        for col in columns:
            self.tree.column(col, anchor="center", width=90)
        self.tree.column("note", width=200)

        # 垂直滾輪
        v_scrollbar = ttk.Scrollbar(
            list_frame, orient=tk.VERTICAL, command=self.tree.yview
        )
        self.tree.configure(yscroll=v_scrollbar.set)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        # 水平滾輪
        h_scrollbar = ttk.Scrollbar(
            list_frame, orient=tk.HORIZONTAL, command=self.tree.xview
        )
        self.tree.configure(xscrollcommand=h_scrollbar.set)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)

        self.tree.pack(fill=tk.BOTH, expand=True)
        btn_frame = tk.Frame(list_frame)
        btn_frame.pack(pady=5)
        btn_modify = tk.Button(btn_frame, text="修改紀錄", command=self.modify_record)
        btn_modify.pack(side=tk.LEFT, padx=5)
        btn_delete = tk.Button(btn_frame, text="刪除紀錄", command=self.delete_record)
        btn_delete.pack(side=tk.LEFT, padx=5)
        btn_stat = tk.Button(
            btn_frame, text="本賽季對手卡組使用比例", command=self.show_opp_deck_pie
        )
        btn_stat.pack(side=tk.LEFT, padx=5)
        self.load_tree_records()

    def refresh_tree_records(self):
        # 清除 Treeview 資料，然後僅載入當前賽季的紀錄
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.load_tree_records()
        self.filter_records()

    def create_statistics_panel(self, parent):
        stats_frame = tk.LabelFrame(parent, text="統計數據")
        stats_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        tk.Label(stats_frame, text="選擇卡組:").pack(padx=5, pady=5)
        self.stats_deck_option = ttk.Combobox(
            stats_frame,
            textvariable=self.stats_deck_var,
            values=self.my_decks,
            state="readonly",
            width=15,
        )
        self.stats_deck_option.pack(padx=5, pady=5)
        self.stats_deck_option.bind(
            "<<ComboboxSelected>>", lambda e: self.update_statistics()
        )
        self.total_label = tk.Label(stats_frame, text="總場數: 0")
        self.total_label.pack(padx=5, pady=5)
        self.win_label = tk.Label(stats_frame, text="勝場數: 0")
        self.win_label.pack(padx=5, pady=5)
        self.win_rate_label = tk.Label(stats_frame, text="勝率: 0%")
        self.win_rate_label.pack(padx=5, pady=5)
        self.first_label = tk.Label(stats_frame, text="先手勝率: 0%")
        self.first_label.pack(padx=5, pady=5)
        self.second_label = tk.Label(stats_frame, text="後手勝率: 0%")
        self.second_label.pack(padx=5, pady=5)
        self.coin_heads_label = tk.Label(stats_frame, text="正面率: 0%")
        self.coin_heads_label.pack(padx=5, pady=5)
        self.coin_tails_label = tk.Label(stats_frame, text="反面率: 0%")
        self.coin_tails_label.pack(padx=5, pady=5)
        self.firstG_win_label = tk.Label(stats_frame, text="先攻中G勝率: 0%")
        self.firstG_win_label.pack(padx=5, pady=5)
        self.expanded_win_label = tk.Label(stats_frame, text="展開中G以外手坑勝率: 0%")
        self.expanded_win_label.pack(padx=5, pady=5)

    def manage_my_decks(self):
        DeckManagementWindow(
            self.root, self.my_decks, "我方卡組", self.update_my_deck_comboboxes
        )

    def manage_opp_decks(self):
        DeckManagementWindow(
            self.root, self.opp_decks, "對方卡組", self.update_opp_deck_comboboxes
        )

    def update_my_deck_comboboxes(self):
        self.my_deck_option["values"] = self.my_decks
        self.stats_deck_option["values"] = self.my_decks
        filter_options = ["全部"] + self.my_decks
        self.filter_option["values"] = filter_options

    def update_opp_deck_comboboxes(self):
        self.opp_deck_option["values"] = self.opp_decks

    def add_record(self):
        my_deck = self.my_deck_var_form.get()
        opp_deck = self.opp_deck_var_form.get()
        result = self.result_var.get()
        turn = self.turn_var.get()
        coin = self.coin_var.get()
        rank = self.rank_var.get()
        forced_first = "是" if (coin == "反面" and turn == "先手") else "否"
        firstG = "是" if self.firstG_var.get() else "否"
        expanded = "是" if self.expanded_var.get() else "否"
        note = self.note_entry.get()
        if not my_deck or not opp_deck:
            messagebox.showerror("錯誤", "請選擇我方和對方的卡組!")
            return
        record = {
            "id": self.record_id_counter,
            "my_deck": my_deck,
            "opp_deck": opp_deck,
            "result": result,
            "turn": turn,
            "rank": rank,
            "coin": coin,
            "forced_first": forced_first,
            "firstG": firstG,
            "expanded": expanded,
            "note": note,
            "season": self.current_season,
        }
        self.record_id_counter += 1
        self.records.append(record)
        if record["season"] == self.current_season:
            self.tree.insert(
                "",
                0,
                iid=str(record["id"]),
                values=(
                    record["my_deck"],
                    record["opp_deck"],
                    record["result"],
                    record["turn"],
                    record["rank"],
                    record["coin"],
                    record["forced_first"],
                    record["firstG"],
                    record["expanded"],
                    record["note"],
                    record["season"],
                ),
            )
        self.note_entry.delete(0, tk.END)
        self.firstG_var.set(False)
        self.expanded_var.set(False)
        self.update_statistics()

    def delete_record(self):
        selection = self.tree.selection()
        if not selection:
            messagebox.showinfo("提示", "請選擇要刪除的紀錄!")
            return
        record_id = int(selection[0])
        for i, rec in enumerate(self.records):
            if rec.get("id") == record_id:
                del self.records[i]
                break
        self.tree.delete(selection[0])
        self.update_statistics()

    def modify_record(self):
        selection = self.tree.selection()
        if not selection:
            messagebox.showinfo("提示", "請選擇要修改的紀錄!")
            return
        record_id = int(selection[0])
        for rec in self.records:
            if rec.get("id") == record_id:
                RecordModifyWindow(self, rec)
                break

    def update_statistics(self):
        selected_deck = self.stats_deck_var.get()
        if not selected_deck:
            self.total_label.config(text="總場數: 0")
            self.win_label.config(text="勝場數: 0")
            self.win_rate_label.config(text="勝率: 0%")
            self.first_label.config(text="先手勝率: 0%")
            self.second_label.config(text="後手勝率: 0%")
            self.coin_heads_label.config(text="正面率: 0%")
            self.coin_tails_label.config(text="反面率: 0%")
            self.firstG_win_label.config(text="先攻中G勝率: 0%")
            self.expanded_win_label.config(text="展開中G以外手坑勝率: 0%")
            return
        filtered = [
            r
            for r in self.records
            if r["season"] == self.current_season and r["my_deck"] == selected_deck
        ]
        total = len(filtered)
        wins = len([r for r in filtered if r["result"] == "勝"])
        win_rate = (wins / total * 100) if total > 0 else 0
        first_games = [r for r in filtered if r["turn"] == "先手"]
        first_wins = len([r for r in first_games if r["result"] == "勝"])
        first_rate = (first_wins / len(first_games) * 100) if first_games else 0
        second_games = [r for r in filtered if r["turn"] == "後手"]
        second_wins = len([r for r in second_games if r["result"] == "勝"])
        second_rate = (second_wins / len(second_games) * 100) if second_games else 0
        coin_heads = len([r for r in filtered if r.get("coin", "正面") == "正面"])
        coin_tails = len([r for r in filtered if r.get("coin", "正面") == "反面"])
        coin_heads_rate = (coin_heads / total * 100) if total > 0 else 0
        coin_tails_rate = (coin_tails / total * 100) if total > 0 else 0
        firstG_recs = [r for r in filtered if r.get("firstG") == "是"]
        firstG_wins = len([r for r in firstG_recs if r["result"] == "勝"])
        firstG_win_rate = (firstG_wins / len(firstG_recs) * 100) if firstG_recs else 0
        expanded_recs = [r for r in filtered if r.get("expanded", "否") == "是"]
        expanded_wins = len([r for r in expanded_recs if r["result"] == "勝"])
        expanded_win_rate = (
            (expanded_wins / len(expanded_recs) * 100) if expanded_recs else 0
        )
        self.total_label.config(text=f"總場數: {total}")
        self.win_label.config(text=f"勝場數: {wins}")
        self.win_rate_label.config(text=f"勝率: {win_rate:.1f}%")
        self.first_label.config(text=f"先手勝率: {first_rate:.1f}%")
        self.second_label.config(text=f"後手勝率: {second_rate:.1f}%")
        self.coin_heads_label.config(text=f"正面率: {coin_heads_rate:.1f}%")
        self.coin_tails_label.config(text=f"反面率: {coin_tails_rate:.1f}%")
        self.firstG_win_label.config(text=f"先攻是否中G勝率: {firstG_win_rate:.1f}%")
        self.expanded_win_label.config(
            text=f"展開中G以外手坑勝率: {expanded_win_rate:.1f}%"
        )

    def filter_records(self):
        filter_val = self.filter_var.get()
        for item in self.tree.get_children():
            self.tree.delete(item)
        for record in self.records:
            if record["season"] == self.current_season:
                if filter_val == "全部" or record.get("my_deck") == filter_val:
                    coin = record.get("coin", "正面")
                    self.tree.insert(
                        "",
                        tk.END,
                        iid=str(record["id"]),
                        values=(
                            record.get("my_deck"),
                            record.get("opp_deck"),
                            record.get("result"),
                            record.get("turn"),
                            record.get("rank", "白金1"),
                            coin,
                            record.get("forced_first"),
                            record.get("firstG"),
                            record.get("expanded", "否"),
                            record.get("note"),
                            record.get("season"),
                        ),
                    )
        self.update_statistics()

    def load_tree_records(self):
        for record in self.records:
            if "id" not in record:
                record["id"] = self.record_id_counter
                self.record_id_counter += 1
            coin = record.get("coin", "正面")
            if record.get("season") == self.current_season:
                self.tree.insert(
                    "",
                    tk.END,
                    iid=str(record["id"]),
                    values=(
                        record.get("my_deck"),
                        record.get("opp_deck"),
                        record.get("result"),
                        record.get("turn"),
                        record.get("rank", "白金1"),
                        coin,
                        record.get("forced_first"),
                        record.get("firstG"),
                        record.get("expanded", "否"),
                        record.get("note"),
                        record.get("season"),
                    ),
                )
        self.update_statistics()

    def load_data(self):
        filename = "card_data.json"
        if os.path.exists(filename):
            try:
                with open(filename, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self.my_decks = data.get("my_decks", [])
                self.opp_decks = data.get("opp_decks", [])
                self.records = data.get("records", [])
                self.current_season = data.get("current_season", "S38")
                for rec in self.records:
                    if "season" not in rec:
                        rec["season"] = "S38"
                if self.records:
                    max_id = max(rec.get("id", 0) for rec in self.records)
                    self.record_id_counter = max_id + 1
            except Exception as e:
                messagebox.showerror("錯誤", f"資料載入失敗: {e}")

    def save_data(self):
        data = {
            "my_decks": self.my_decks,
            "opp_decks": self.opp_decks,
            "records": self.records,
            "current_season": self.current_season,
        }
        try:
            with open("card_data.json", "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
        except Exception as e:
            messagebox.showerror("錯誤", f"資料儲存失敗: {e}")

    def refresh_tree_records(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.load_tree_records()
        self.filter_records()

    def show_opp_deck_pie(self):
        season_records = [
            r for r in self.records if r.get("season") == self.current_season
        ]
        if not season_records:
            messagebox.showinfo("提示", "當前賽季尚無資料")
            return
        OpponentDeckPieChart(self, season_records)

    def on_close(self):
        self.save_data()
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = CardRecordApp(root)
    root.mainloop()
