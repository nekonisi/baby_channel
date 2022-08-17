from sqlalchemy import Table, Column, Integer, String, MetaData
 
meta = MetaData()
users = Table('Users', meta,
              Column('id', Integer, primary_key=True),
              Column('name', String),
              Column('age', Integer)
              )
 
print('# Usersテーブルの確認')
print(meta.tables['Users'])
 
print('# すべてのテーブルの確認')
for table in meta.tables:
    print(table)
 
print('# columns、もしくはcでカラム名の参照が可能')
print(users.columns.name)
print(users.c.name)
 
print('# すべてのカラムの確認')
for col in users.c:
    print(col)
 
print('# primary_keyで主キーを参照可能')
for pk in users.primary_key:
    print(pk)
 
print('# その他のカラムの属性の確認')
print(users.c.id.name)
print(users.c.id.type)
print(users.c.id.nullable)
print(users.c.id.primary_key)