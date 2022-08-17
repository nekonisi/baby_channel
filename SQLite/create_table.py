import sqlite3

# TEST.dbを作成する
# すでに存在していれば、それにアスセスする。
dbname = 'TEST.db'
conn = sqlite3.connect(dbname)

# カーソルを作成
cur = conn.cursor()

cur.execute(
    'CREATE TABLE items(id INTEGER PRIMARY KEY AUTOINCREMENT, name STRING, price INTEGER)'
)
# データベースへのコネクションを閉じる。(必須)
conn.close()