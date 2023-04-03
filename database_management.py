from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session
from sqlalchemy import MetaData


#%%
engine = create_engine("sqlite+pysqlite:///keystroke_database.db", echo=True)

#%%
with engine.begin() as conn:
    conn.execute(
        text("INSERT INTO some_table (x, y) VALUES (:x, :y)"),
        [{"x": 6, "y": 8}, {"x": 9, "y": 10}],
    )
#%%
with engine.connect() as conn:
    result = conn.execute(text("SELECT x,y FROM some_table"))
    for x, y in result:
        print(f"x: {x}, y: {y}")
#%%
with engine.connect() as conn:
    result = conn.execute(text("SELECT x, y FROM some_table WHERE y> :y"), {"y": 2})
    for row in result:
        print(f"x: {row.x} y: {row.y}")
#%%
with engine.connect() as conn:
    conn.execute(
        text("INSERT INTO some_table (x, y) VALUES (:x, :y)"),
        [{"x": 11, "y": 12}, {"x": 13, "y": 14}],
    )
    conn.commit()
#%%
stmt = text("SELECT x, y FROM some_table WHERE y > :y ORDER BY x, y")
with Session(engine) as session:
    result = session.execute(stmt, {"y": 6})
    for row in result:
        print(f"x: {row.x} y: {row.y}")
#%%
with Session(engine) as session:
    result = session.execute(
        text("UPDATE some_table SET y=:y WHERE x=:x"),
        [{"x": 9, "y": 11}, {"x": 13, "y": 15}],
    )
    session.commit()
#%%
metadata_obj = MetaData()
#%%
from sqlalchemy import Table, Column, Integer, String


user_table = Table(
    "user_account",
    metadata_obj,
    Column("id", Integer, primary_key=True),
    Column("name", String(30)),
    Column("fullname", String),
)
#%%
from sqlalchemy import ForeignKey
address_table = Table(
    "address",
    metadata_obj,
    Column("id", Integer, primary_key=True),
    Column("user_id", ForeignKey("user_account.id"), nullable=False),
    Column("email_address", String, nullable=False)
)
#%%
metadata_obj.drop_all(engine)
#%%
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass
#%%
from typing import List, Optional
from sqlalchemy.orm import Mapped, mapped_column, relationship


class User(Base):
    __tablename__ = "user_account"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30))
    fullname: Mapped[Optional[str]]

    addresses: Mapped[List["Address"]] = relationship(back_populates="user")

    def __repr__(self):
        return f"User(id={self.id!r}, name={self.name!r}, fullname={self.fullname!r})"


class Address(Base):
    __tablename__ = "address"

    id: Mapped[int] = mapped_column(primary_key=True)
    email_address: Mapped[str]
    user_id = mapped_column(ForeignKey("user_account.id"))

    user: Mapped[User] = relationship(back_populates="addresses")

    def __repr__(self) -> str:
        return f"Address(id={self.id!r}, email_address={self.email_address!r})"


Base.metadata.create_all(engine)
#%%
some_table = Table("some_table", metadata_obj, autoload_with=engine)
#%%
from sqlalchemy import insert
stmt = insert(user_table).values(name="spongebob", fullname="Spongebob Squarepants")

compiled = stmt.compile()
#%%
with engine.connect() as conn:
    result = conn.execute(stmt)
    conn.commit()
#%%
with engine.connect() as conn:
    result = conn.execute(
        insert(user_table),
        [
            {"name": "sandy", "fullname": "Sandy Cheeks"},
            {"name": "patric", "fullname": "Patrick Star"},
        ],
    )
    conn.commit()
#%%
from sqlalchemy import select, bindparam

scalar_subq = (
    select(user_table.c.id).where(user_table.c.name == bindparam("username")).scalar_subquery()
)
with engine.connect() as conn:
    result = conn.execute(
        insert(address_table).values(user_id=scalar_subq),
        [
            {
                "username": "spongebob",
                "email_address": "spongebob@sqlalchemy.org",
            },
            {"username": "sandy", "email_address": "sandy@sqlalchemy.org"},
            {"username": "sandy", "email_address": "sandy@squirrelpower.org"},
        ],
    )
    conn.commit()
#%%
insert_stmt = insert(address_table).returning(
    address_table.c.id, address_table.c.email_address
)
print(insert_stmt)
#%%
select_stmt = select(user_table.c.id, user_table.c.name + "@aol.com")
insert_stmt = insert(address_table).from_select(
    ["user_id", "email_address"], select_stmt)
print(insert_stmt.returning(address_table.c.id, address_table.c.email_address))
#%%
