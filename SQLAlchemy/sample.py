from sqlalchemy import create_engine
 
engine = create_engine('sqlite://:memory:')
 
# 接続する
with engine.connect() as con:
 
    # テーブルの作成
    con.execute("CREATE TABLE USERS(id INTEGER PRIMARY KEY, name TEXT, age INTEGER)")
 
    # Insert文を実行する
    con.execute("INSERT INTO USERS (id, name, age) VALUES(1, 'Kuro', '33')")
    con.execute("INSERT INTO USERS (id, name, age) VALUES(2, 'Sato', '27')")
 
    # Select文を実行する
    rows = con.execute("select * from users;")
    for row in rows:
        print(row)