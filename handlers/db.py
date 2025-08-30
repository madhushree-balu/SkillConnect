import sqlite3
from typing import Union, Optional
import models


class DB:
    def __init__(self, db_file="storage.sqlite3"):
        self.db_file = db_file
        self.connection: sqlite3.Connection | None = None

    def connect(self):
        self.connection = sqlite3.connect(self.db_file)
        return self
    
    def close(self):
        if self.connection is not None:
            self.connection.close()
        return self
    
    def commit(self):
        if self.connection is not None:
            self.connection.commit()
        return self
    
    def __enter__(self) -> sqlite3.Connection:
        if self.connection is None:
            self.connection = sqlite3.connect(self.db_file)
        return self.connection
    
    def __exit__(self, exc_type, exc_value, traceback):
        self.close()
        self.connection = None
    
    def execute(self, query, params: tuple = tuple(), commit=True):
        if self.connection is None:
            self.connection = sqlite3.connect(self.db_file)
        
        cursor = self.connection.cursor()
        cursor.execute(query, params)
        
        if commit:
            self.commit()

        return cursor

