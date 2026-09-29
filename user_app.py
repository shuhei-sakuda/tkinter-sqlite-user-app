# Tkinterを読み込む
import tkinter as tk
# メッセージボックスを使えるようにする
from tkinter import messagebox
# SQLiteを使えるようにする
import sqlite3
root = tk.Tk()
root.title("ユーザー管理アプリ")
# SQLiteデータベースに接続
conn = sqlite3.connect("new_users.db")
# データベースの行を列名で取得できるようにする
conn.row_factory = sqlite3.Row
# SQLを実行するためのカーソルを作成
cursor = conn.cursor()
# usersテーブルが存在しなければ作成
cursor.execute(""" CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL ) """)
# テーブル作成を確定
conn.commit()
# 編集対象のListboxの位置を保存する
edit_index = None
# Listboxの位置とデータベースのIDを対応させるリスト
user_ids = []
# ユーザー一覧を表示するListboxを作成
listbox = tk.Listbox(root, width=30)
listbox.pack()
# データベースからユーザーを取得
cursor.execute("SELECT * FROM users")
rows = cursor.fetchall()
# 取得したユーザーをListboxに表示
for row in rows:
    listbox.insert(tk.END, row["name"])
    user_ids.append(row["id"])
# ユーザー名を入力する欄
entry = tk.Entry(root,  width=30, relief="solid", borderwidth=2)
entry.pack()
# ユーザーを登録する
def add_user():
    # 入力欄から名前を取得
    name = entry.get()
    if name != "":
        # SQLiteにユーザーを登録
        cursor.execute(""" INSERT INTO users (name) VALUES (?)""", (name,))
        # データベースへの変更を確定
        conn.commit()
        # 画面とIDの一覧を更新
        user_ids.append(cursor.lastrowid)
        listbox.insert(tk.END, name)
        entry.delete(0, tk.END)
    else:
        # 名前が入力されていない場合は警告を表示
        messagebox.showwarning("入力エラー", "名前を入力してください")
        entry.focus_set()
# ユーザーを削除する
def delete_user():
    # 選択されたユーザーを取得
    selected = listbox.curselection()
    if selected:
        db_id = user_ids[selected[0]]
        # データベースからユーザーを削除
        cursor.execute(""" DELETE FROM users WHERE id = ?""", (db_id,))
        # データベースへの削除を確定
        conn.commit()
        # Listboxからユーザーを削除
        listbox.delete(selected[0])
        # ユーザーIDの一覧からも削除
        user_ids.pop(selected[0])
    else:
        messagebox.showwarning("選択エラー", "名前を選択してください")
# ユーザーを編集する
def edit_user():
    global edit_index
    # 選択されたユーザーを取得
    selected = listbox.curselection()
    if selected:
        # 選択されたユーザーのListbox上の位置を保存
        edit_index = selected[0]
        # 選択されたユーザーの名前を取得
        name = listbox.get(selected[0])
        # 入力欄を空にする
        entry.delete(0, tk.END)
        # 選択された名前を入力欄に表示
        entry.insert(0, name)
    else:
        messagebox.showwarning("選択エラー", "名前を選択してください")
# ユーザー情報を更新する
def update_user():
    global edit_index
    # 入力欄から新しい名前を取得
    new_name = entry.get()
    # 編集対象があり、新しい名前が入力され、元の名前と異なる場合
    if edit_index is not None and new_name != "" and listbox.get(edit_index) != new_name:
        # Listboxの位置からデータベースのIDを取得
        db_id = user_ids[edit_index]
        # データベースのユーザー名を更新
        cursor.execute("""UPDATE users SET name = ? WHERE id = ?""", (new_name, db_id))
        # データベースへの更新を確定
        conn.commit()
        # Listboxから古い名前を削除
        listbox.delete(edit_index)
        # Listboxに新しい名前を表示
        listbox.insert(edit_index, new_name)
        # 入力欄を空にする
        entry.delete(0, tk.END)
        # 編集状態を解除
        edit_index = None
    elif edit_index is None:
        messagebox.showwarning("選択エラー", "更新したい名前を選択し、編集ボタンを押して、名前を編集してもう一度更新ボタンを押してください")
    # 新しい名前が入力されていない場合
    elif "" == entry.get():
        messagebox.showwarning("入力エラー", "名前を入力してください")
    # 新しい名前が元の名前と同じ場合
    elif listbox.get(edit_index) == new_name:
        messagebox.showwarning("入力エラー", "名前が同じです")
button = tk.Button(root, text="登録", command=add_user)
button.pack()
delete_button = tk.Button(root, text="削除", command=delete_user)
delete_button.pack()
edit_button = tk.Button(root, text="編集", command=edit_user)
edit_button.pack()
update_button = tk.Button(root, text="更新", command=update_user)
update_button.pack()
# アプリ終了時の処理
def on_close():
    # データベースとの接続を閉じる
    conn.close()
    root.destroy()
# ウィンドウを閉じるときにon_closeを実行
root.protocol("WM_DELETE_WINDOW", on_close)
root.mainloop()
