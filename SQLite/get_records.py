import sqlite3

# TEST.dbを作成する
# すでに存在していれば、それにアスセスする。
dbname = 'TEST.db'
conn = sqlite3.connect(dbname)

cur = conn.cursor()

# データ検索
cur.execute('SELECT * FROM items')

# 取得したデータはカーソルの中に入る
for row in cur:
    print(row)

# データベースへのコネクションを閉じる。(必須)
conn.close()