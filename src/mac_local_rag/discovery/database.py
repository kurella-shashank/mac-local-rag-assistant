import sqlite3
from pathlib import Path
from .scanner import FileRecord


class MetadataDatabase:
    def __init__(self, database_path: Path):
        self.database_path = Path(database_path)
        self.database_path.parent.mkdir(
            parents=True, exist_ok=True
        )
        self.initialize()

    def connect(self):
        return sqlite3.connect(self.database_path)

    def initialize(self):
        with self.connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS filesystem_entries (
                    source_root TEXT NOT NULL,
                    relative_path TEXT NOT NULL,
                    name TEXT NOT NULL,
                    kind TEXT NOT NULL,
                    extension TEXT NOT NULL,
                    size_bytes INTEGER NOT NULL,
                    modified_at REAL NOT NULL,
                    PRIMARY KEY (source_root, relative_path)
                )
                """
            )

            connection.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_entries_name
                ON filesystem_entries(name)
                """
            )

    def save_scan(
        self, source_root: str, records: list[FileRecord]
    ):
        if any(
            record.source_root != source_root
            for record in records
        ):
            raise ValueError("Records belong to another root.")

        with self.connect() as connection:
            connection.execute(
                "DELETE FROM filesystem_entries WHERE source_root = ?",
                (source_root,),
            )

            connection.executemany(
                """
                INSERT INTO filesystem_entries
                (
                    source_root, relative_path, name,
                    kind, extension, size_bytes, modified_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    (
                        record.source_root,
                        record.relative_path,
                        record.name,
                        record.kind,
                        record.extension,
                        record.size_bytes,
                        record.modified_at,
                    )
                    for record in records
                ],
            )

    def search(self, keyword: str, limit: int = 50):
        with self.connect() as connection:
            connection.row_factory = sqlite3.Row

            rows = connection.execute(
                """
                SELECT *
                FROM filesystem_entries
                WHERE instr(lower(name), lower(?)) > 0
                ORDER BY name, source_root, relative_path
                LIMIT ?
                """,
                (keyword, limit),
            ).fetchall()

            return [dict(row) for row in rows]

    def count_entries(self):
        with self.connect() as connection:
            return connection.execute(
                """
                SELECT
                    COUNT(*) AS total,
                    SUM(CASE WHEN kind = 'file'
                        THEN 1 ELSE 0 END) AS files,
                    SUM(CASE WHEN kind = 'directory'
                        THEN 1 ELSE 0 END) AS directories
                FROM filesystem_entries
                """
            ).fetchone()
