from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
 
# DB接続
engine = create_engine('sqlite:///:memory:')
 
# Base
Base = declarative_base()
 
 
# テーブルクラスを定義
class User(Base):
    """
    Userテーブルクラス
    """
 
    # テーブル名
    __tablename__ = 'users'
 
    # 個々のカラムを定義
    id = Column(Integer, primary_key=True)
    name = Column(String)
    age = Column(Integer)
 
 
# テーブルクラスのテーブルを生成
Base.metadata.create_all(engine)
 
# セッション生成
Session = sessionmaker(bind=engine)
session = Session()
 
 
# 挿入用レコード作成
suzuki = User(name="Suzuki", age=19)
session.add(suzuki) # insert処理
session.commit()    # commit
 
# select * from users;
users_obj = session.query(User).all()
for user in users_obj:
    print(user.id)
    print(user.name)
    print(user.age)
 
# select * from users where id = 1;
suzuki = session.query(User).get(1)
suzuki.age = 20
 
# update
session.add(suzuki)
session.commit()

# select * from users;
users_obj = session.query(User).all()
for user in users_obj:
    print(user.id)
    print(user.name)
    print(user.age)

# delete
session.delete(suzuki)

# select * from users;
users_obj = session.query(User).all()
for user in users_obj:
    print(user.id)
    print(user.name)
    print(user.age)
