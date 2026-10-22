"""Small database timestamp used by the player-triggered publication workflow."""


def stamp_database(connection, snapshot_id, save_id, data_updated_at):
    connection.execute("""CREATE TABLE IF NOT EXISTS data_sync_metadata (
        snapshot_id TEXT PRIMARY KEY,
        save_id TEXT NOT NULL,
        data_updated_at TEXT NOT NULL
    )""")
    connection.execute("""INSERT INTO data_sync_metadata(snapshot_id,save_id,data_updated_at)
        VALUES(?,?,?) ON CONFLICT(snapshot_id) DO UPDATE SET
        save_id=excluded.save_id,data_updated_at=excluded.data_updated_at""",
        (snapshot_id, save_id, data_updated_at))
