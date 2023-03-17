import sqlite3


class DBManager:
    def __init__(self, db_name):
        self.dbname = db_name
        self.conn = sqlite3.connect(self.dbname)
        self.cursor = self.conn.cursor()

        self.cursor.execute(f"CREATE TABLE IF NOT EXISTS FRIENDS(Friend_ID INTEGER PRIMARY KEY, Username, Friend_UID)")
        self.conn.commit()
