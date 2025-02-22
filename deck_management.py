import tkinter as tk 
from tkinter import messagebox, simpledialog
from tools import center_window
from edit_window import EditNameWindow

class DeckManagementWindow(tk.Toplevel):
    def __init__(self, master, deck_list, deck_type, update_callback):
        super().__init__(master)
        self.title(f"{deck_type}管理")
        self.deck_list = deck_list
        self.deck_type = deck_type
        self.update_callback = update_callback
        self.geometry("400x300")
        self.create_widgets()
        center_window(self, master)

    def create_widgets(self):
        self.listbox = tk.Listbox(self)
        self.listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        for deck in self.deck_list:
            self.listbox.insert(tk.END, deck)
        
        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=5)
        tk.Button(btn_frame, text="新增", command=self.add_deck).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="修改", command=self.modify_deck).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="刪除", command=self.delete_deck).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="關閉", command=self.destroy).pack(side=tk.LEFT, padx=5)

    def add_deck(self):
        new_name_window = EditNameWindow(self, "新增卡組")
        new_deck = new_name_window.new_name
        if not new_deck:
            return
        if new_deck in self.deck_list:
            messagebox.showinfo("提示", "該卡組已存在!")
            return

        self.deck_list.append(new_deck)
        self.listbox.insert(tk.END, new_deck)
        self.update_callback()

    def modify_deck(self):
        selection = self.listbox.curselection()
        if not selection:
            messagebox.showinfo("提示", "請選擇要修改的卡組!")
            return
        index = selection[0]
        current_name = self.deck_list[index]
        new_name_window = EditNameWindow(self, "修改卡組名稱", current_name)
        new_name = new_name_window.new_name
        if not new_name:
            return
        if new_name in self.deck_list:
            messagebox.showinfo("提示", "該卡組已存在!")
            return
        self.deck_list[index] = new_name
        self.listbox.delete(index)
        self.listbox.insert(index, new_name)
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


class SeasonManagementWindow(tk.Toplevel):
    def __init__(self, app):
        super().__init__(app.root)
        self.app = app
        self.title("賽季管理")
        self.geometry("300x300")
        self.create_widgets()
        center_window(self, app.root)

    def create_widgets(self):
        tk.Label(self, text="賽季列表:").pack(pady=5)
        self.season_listbox = tk.Listbox(self)
        self.season_listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        self.refresh_season_list()
        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=5)
        tk.Button(btn_frame, text="載入賽季", command=self.load_season).pack(
            side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="新增賽季", command=self.add_season).pack(
            side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="刪除賽季資料", command=self.delete_season).pack(
            side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="關閉", command=self.destroy).pack(
            side=tk.LEFT, padx=5)

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
        new_season = simpledialog.askstring("新增賽季或盃賽名稱", parent=self)
        if new_season:
            new_season = new_season.strip()
            # 取得所有現有的賽季
            existing_seasons = {rec.get("season", self.app.current_season) for rec in self.app.records}
            existing_seasons.add(self.app.current_season)
            if new_season in existing_seasons:
                messagebox.showinfo("提示", "該賽季已存在！")
            else:
                # 新增賽季後，直接切換至該賽季（你也可以僅將它加入列表，而不立即切換）
                self.app.current_season = new_season
                self.app.season_label.config(text=new_season)
                self.app.refresh_tree_records()
                self.refresh_season_list()
                messagebox.showinfo("提示", f"已新增並切換到賽季 {new_season}")

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
