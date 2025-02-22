import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from deck_management import DeckManagementWindow, SeasonManagementWindow
from record_modify import RecordModifyWindow
from data_manager import load_data, save_data
from charts import OpponentDeckPieChart, MyDeckPieChart
from tools import center_window
import sys

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
        self.sort_descending = False
        self.current_season = "S38"  # 預設賽季
        self.stats_deck_var = tk.StringVar()
        self.filter_var = tk.StringVar(value="全部")

        data = load_data()
        if data is not None:
            self.my_decks, self.opp_decks, self.records, self.current_season = data
        else:
            # 若讀取失敗，不覆蓋原檔案
            messagebox.showwarning("資料載入失敗")

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

        tk.Label(form_frame, text="是否卡手:").grid(row=2, column=4, padx=5, pady=5, sticky="e")
        self.card_stuck_var = tk.BooleanVar()
        self.card_stuck_cb = tk.Checkbutton(form_frame, variable=self.card_stuck_var)
        self.card_stuck_cb.grid(row=2, column=5, padx=5, pady=5, sticky="w")

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
            "card_stuck",
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
        self.tree.heading("card_stuck", text="是否卡手", anchor="center")
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
        btn_my_deck_stat = tk.Button(btn_frame, text="本賽季我方卡組使用比例", command=self.show_my_deck_pie)
        btn_my_deck_stat.pack(side=tk.LEFT, padx=5)
        btn_sort = tk.Button(
            btn_frame,
            text="由新至舊" if self.sort_descending else "由舊至新",
            command=self.toggle_sort_order,
        )
        btn_sort.pack(side=tk.LEFT, padx=5)
        self.sort_button = btn_sort
        self.load_tree_records()

    def toggle_sort_order(self):
        self.filter_records()
        self.sort_descending = not self.sort_descending
        self.sort_button.config(text="由新至舊" if self.sort_descending else "由舊至新")

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
        self.card_stuck_rate_label = tk.Label(stats_frame, text="卡手率: 0%")
        self.card_stuck_rate_label.pack(padx=5, pady=5)

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
        card_stuck = "是" if self.card_stuck_var.get() else "否"
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
            "card_stuck": card_stuck,
            "note": note,
            "season": self.current_season,
        }
        self.record_id_counter += 1  # 保證下次不會重複使用相同 id
        self.records.append(record)
        if record["season"] == self.current_season:
            self.tree.insert("",  0,  iid=str(record["id"]),
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
                    record["card_stuck"],
                    record["note"],
                    record["season"],
                ),
            )
        self.note_entry.delete(0, tk.END)
        self.firstG_var.set(False)
        self.expanded_var.set(False)
        self.card_stuck_var.set(False)
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
            self.card_stuck_rate_label.config(text="卡手率: 0%")
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
        card_stuck = len([r for r in filtered if r.get("card_stuck", "否") == "是"])
        card_stuck_rate = (card_stuck / total * 100) if total > 0 else 0

        self.total_label.config(text=f"總場數: {total}")
        self.win_label.config(text=f"勝場數: {wins}")
        self.win_rate_label.config(text=f"勝率: {win_rate:.1f}%")
        self.first_label.config(text=f"先手勝率: {first_rate:.1f}%")
        self.second_label.config(text=f"後手勝率: {second_rate:.1f}%")
        self.coin_heads_label.config(text=f"正面率: {coin_heads_rate:.1f}%")
        self.coin_tails_label.config(text=f"反面率: {coin_tails_rate:.1f}%")
        self.firstG_win_label.config(text=f"先攻中G勝率: {firstG_win_rate:.1f}%")
        self.expanded_win_label.config(
            text=f"展開中G以外手坑勝率: {expanded_win_rate:.1f}%"
        )
        self.card_stuck_rate_label.config(text=f"卡手率: {card_stuck_rate:.1f}%")

    def filter_records(self):
        filter_val = self.filter_var.get()
        # 先從當前賽季的紀錄中篩選出符合條件的紀錄
        filtered_records = [
            r for r in self.records if r.get("season") == self.current_season
        ]
        if filter_val != "全部":
            filtered_records = [
                r for r in filtered_records if r.get("my_deck") == filter_val
            ]
        # 依據 sort_descending 進行排序：假設 id 越大表示越新
        sorted_records = sorted(
            filtered_records, key=lambda r: r["id"], reverse=self.sort_descending
        )
        # 清空 Treeview
        for item in self.tree.get_children():
            self.tree.delete(item)
        # 插入排序後的資料
        for record in sorted_records:
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
                    record.get("card_stuck","否"),
                    record.get("note"),
                    record.get("season"),
                ),
            )
        self.update_statistics()

    def ensure_unique_ids(self):
        # 先找出所有有效的 id，並取得最大值
        max_id = -1
        for record in self.records:
            rec_id = record.get("id")
            if isinstance(rec_id, int):
                max_id = max(max_id, rec_id)
        # 如果沒有任何 id，設定 max_id 為 -1
        if max_id < 0:
            max_id = -1

        # 建立一個集合來追蹤已使用的 id
        seen = set()
        for record in self.records:
            rec_id = record.get("id")
            # 若沒有 id、非整數或已重複，則重新分配一個新的 id
            if not isinstance(rec_id, int) or rec_id in seen:
                max_id += 1
                record["id"] = max_id
            seen.add(record["id"])
        # 更新 record_id_counter 為最大 id 的下一個數字
        self.record_id_counter = max_id + 1

    def load_tree_records(self):
        # 清除現有項目，避免重複插入
        for item in self.tree.get_children():
            self.tree.delete(item)

        self.ensure_unique_ids()
        # 篩選出當前賽季的紀錄
        filtered_records = [
            r for r in self.records if r.get("season") == self.current_season
        ]
        # 根據 id 排序（假設 id 越大表示越新）
        sorted_records = sorted(
            filtered_records, key=lambda r: r["id"], reverse=self.sort_descending
        )
        # 插入資料到 Treeview
        for record in sorted_records:
            coin = record.get("coin", "正面")
            self.tree.insert(
                "",
                0,
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
                    record.get("card_stuck","否"),
                    record.get("note"),
                    record.get("season"),
                ),
            )
        self.update_statistics()

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


    def show_my_deck_pie(self):
        # 篩選出當前賽季的所有紀錄
        season_records = [r for r in self.records if r.get("season") == self.current_season]
        if not season_records:
            messagebox.showinfo("提示", "當前賽季尚無資料")
            return
        from charts import MyDeckPieChart  # 確保正確引用

        MyDeckPieChart(self, season_records)


    def on_close(self):
        data=load_data()
        if data is not None:
            save_data(self.my_decks, self.opp_decks, self.records, self.current_season)
        self.root.destroy()

        sys.exit(0)
