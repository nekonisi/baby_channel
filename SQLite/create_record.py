import sqlite3

# TEST.dbを作成する
# すでに存在していれば、それにアスセスする。
dbname = 'TEST.db'
conn = sqlite3.connect(dbname)

cur = conn.cursor()
# データ登録
cur.execute('INSERT INTO items values(0, "りんご", 100)')

# コミットしないと登録が反映されない
conn.commit()
# データベースへのコネクションを閉じる。(必須)
conn.close()