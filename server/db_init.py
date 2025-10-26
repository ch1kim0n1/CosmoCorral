"""Database initialization and models using peewee.

Creates an SQLite `app.db` beside this file using the sqlite ext database
so JSONField is available. Provides two models: Device and Report.

Assumptions:
- The field name `reson` in the user's spec looked like a typo; I created it
  as `reason` (string). If you prefer the exact `reson` name, tell me and I
  will change it.
"""
from __future__ import annotations

import os
import json
from datetime import datetime
from typing import Optional
import uuid

from peewee import (
    Model,
    CharField,
    DateTimeField,
    IntegerField,
    TextField,
    ForeignKeyField,
    UUIDField,
)
from playhouse.sqlite_ext import SqliteExtDatabase, JSONField


BASE_DIR = os.path.dirname(__file__)
DB_FILENAME = os.path.join(BASE_DIR, "app.db")

# Use the sqlite extension database so we can use JSONField on SQLite.
db = SqliteExtDatabase(DB_FILENAME)


class BaseModel(Model):
    class Meta:
        database = db


class Device(BaseModel):
    id = UUIDField(primary_key=True, default=uuid.uuid4)
    name = CharField(max_length=255)
    access_code = CharField(max_length=255, null=True)
    last_online = DateTimeField(null=True)
    last_session_time = IntegerField(null=True)  # seconds, nullable

    def __str__(self) -> str:  # helpful for debugging
        return f"Device(id={self.id}, name={self.name})"


class Report(BaseModel):
    id = UUIDField(primary_key=True, default=uuid.uuid4)
    # ForeignKeyField will reference the Device primary key (UUID)
    device = ForeignKeyField(Device, backref="reports", on_delete="CASCADE")
    timestamp = DateTimeField(default=datetime.utcnow)
    reason = TextField(null=True)
    message = TextField(null=True)
    screen_shot_id = CharField(max_length=255, null=True)
    data = JSONField(null=True)

    def __str__(self) -> str:
        return f"Report(id={self.id}, device_id={self.device.id}, ts={self.timestamp})"


def db_connect(create_tables: bool = True, path: Optional[str] = None):
    """Ensure a connection to the SQLite database and optionally create tables.

    - If `path` is provided, the module-level `db` will be re-initialized to
      point to that file.
    - If the file did not exist before connecting and `create_tables` is
      True, the Device and Report tables will be created.

    Returns the connected database object.
    """
    global db
    db_path = DB_FILENAME if path is None else path

    # If user passed a different path, re-init the db object to point there.
    if path is not None:
        if not db.is_closed():
            db.close()
        db.init(path)

    # If the file does not exist we will need to create tables after connect.
    need_create = not os.path.exists(db_path)

    db.connect(reuse_if_open=True)
    if create_tables and need_create:
        db.create_tables([Device, Report])

    return db


def initialize_db(path: Optional[str] = None) -> str:
    """Compatibility wrapper that initializes the DB and returns its path."""
    db_connect(create_tables=True, path=path)
    return DB_FILENAME if path is None else path


if __name__ == "__main__":
    print(f"Initializing DB at: {DB_FILENAME}")
    path = initialize_db()

    # Quick verification: print counts
    db.connect(reuse_if_open=True)
    db.close()
    print("Database initialized successfully.")
