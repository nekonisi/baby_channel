from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# DB接続
engine = create_engine('sqlite:///test.db')
 
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