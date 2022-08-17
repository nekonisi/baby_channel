import sqlite3

# TEST.dbを作成する
# すでに存在していれば、それにアスセスする。
dbname = 'TEST.db'
conn = sqlite3.connect(dbname)

cur = conn.cursor()
# データ登録
inserts = [
    (1, "みかん", 80),
    (2, "ぶどう", 150),
    (3, "バナナ", 60)
]

# 複数データ登録
cur.executemany('INSERT INTO items values(?, ?, ?)', inserts)
conn.commit()
# データベースへのコネクションを閉じる。(必須)
conn.close()