import sys, os

def center_window(window, parent):
    window.update_idletasks()  # 確保取得正確尺寸
    # 取得主視窗的位置與尺寸
    parent_x = parent.winfo_x()
    parent_y = parent.winfo_y()
    parent_width = parent.winfo_width()
    parent_height = parent.winfo_height()
    # 取得跳出視窗的尺寸
    window_width = window.winfo_width()
    window_height = window.winfo_height()
    # 計算新的 x, y 座標
    x = parent_x + (parent_width - window_width) // 2
    y = parent_y + (parent_height - window_height) // 2
    window.geometry(f"+{x}+{y}")


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


def my_deck_name():
    my_decks = [
        "刻魔蛇眼",
        "刻魔尤貝爾",
        "白森刻魔聖徒",
        "刻魔珠淚",
        "肅聲",
        "天盃龍",
        "閃刀姬",
    ]
    return my_decks

def  opp_deck_name():
    opp_decks = [
        "刻魔尤貝爾",
        "刻魔聖徒蛇眼",
        "刻魔白森聖徒",
        "刻魔珠淚",
        "60GS",
        "天盃龍",
        "反主流",
        "大法師",
        "60烙印",
        "霸王幻奏" "白銀城",
        "刻魔聖徒消防隊",
        "龍輝巧",
        "英雄",
        "魔式甜點",
        "肅聲",
        "百夫長" "六花",
        "魔術師",
        "人偶FTK",
        "荷魯斯強攻",
        "神碑",
        "雙子雷精靈",
        "光道FTK",
        "天威相劍",
    ]

    return opp_decks