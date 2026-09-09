import sqlite3

from pathlib import Path


BASE_DIR = (
    Path(__file__)
    .resolve()
    .parent
    .parent
)

DB_PATH = (
    BASE_DIR
    / "database"
    / "classroom.db"
)


def get_connection():
    connection = sqlite3.connect(
        DB_PATH
    )

    connection.row_factory = (
        sqlite3.Row
    )

    connection.execute(
        "PRAGMA foreign_keys = ON"
    )

    return connection


def init_database():
    DB_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS analysis_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,

            source_type TEXT NOT NULL,
            source_name TEXT,

            persons INTEGER DEFAULT 0,

            total_seats INTEGER DEFAULT 0,
            occupied_seats INTEGER DEFAULT 0,
            empty_seats INTEGER DEFAULT 0,

            occupancy_rate REAL DEFAULT 0,

            fps REAL,

            output_path TEXT,

            created_at TIMESTAMP
                DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS seat_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,

            session_id INTEGER NOT NULL,

            seat_id TEXT NOT NULL,
            status TEXT NOT NULL,

            confidence REAL,

            FOREIGN KEY (
                session_id
            )
            REFERENCES analysis_sessions(id)
            ON DELETE CASCADE
        )
    """)

    connection.commit()
    connection.close()

    print(
        f"Database ready: {DB_PATH}"
    )


def save_analysis_session(
    source_type,
    source_name,
    persons,
    statistics,
    output_path=None,
    fps=None
):
    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO analysis_sessions (
            source_type,
            source_name,
            persons,
            total_seats,
            occupied_seats,
            empty_seats,
            occupancy_rate,
            fps,
            output_path
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            source_type,
            source_name,
            persons,
            statistics[
                "total_seats"
            ],
            statistics[
                "occupied_seats"
            ],
            statistics[
                "empty_seats"
            ],
            statistics[
                "occupancy_rate"
            ],
            fps,
            output_path
        )
    )

    session_id = (
        cursor.lastrowid
    )

    connection.commit()
    connection.close()

    return session_id


def save_seat_results(
    session_id,
    occupancy_results,
    mappings=None
):
    connection = get_connection()

    cursor = connection.cursor()

    confidence_map = {}

    if mappings:
        for mapping in mappings:

            seat_id = mapping.get(
                "seat_id"
            )

            if seat_id is not None:

                confidence = mapping.get(
                    "confidence"
                )

                # Nếu có nhiều person map vào
                # cùng một seat, lấy confidence cao nhất
                if (
                    seat_id not in confidence_map
                    or (
                        confidence is not None
                        and confidence >
                        (
                            confidence_map[
                                seat_id
                            ]
                            or 0
                        )
                    )
                ):
                    confidence_map[
                        seat_id
                    ] = confidence

    for seat in occupancy_results:

        seat_id = seat[
            "seat_id"
        ]

        cursor.execute(
            """
            INSERT INTO seat_results (
                session_id,
                seat_id,
                status,
                confidence
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                session_id,
                seat_id,
                seat[
                    "status"
                ],
                confidence_map.get(
                    seat_id
                )
            )
        )

    connection.commit()
    connection.close()


def get_history():
    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            id,
            source_type,
            source_name,
            persons,
            total_seats,
            occupied_seats,
            empty_seats,
            occupancy_rate,
            fps,
            output_path,
            created_at
        FROM analysis_sessions
        ORDER BY id DESC
    """)

    rows = cursor.fetchall()

    connection.close()

    return [
        dict(row)
        for row in rows
    ]


def get_session_detail(
    session_id
):
    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT *
        FROM analysis_sessions
        WHERE id = ?
        """,
        (
            session_id,
        )
    )

    session = cursor.fetchone()

    if session is None:
        connection.close()
        return None

    cursor.execute(
        """
        SELECT
            seat_id,
            status,
            confidence
        FROM seat_results
        WHERE session_id = ?
        ORDER BY seat_id
        """,
        (
            session_id,
        )
    )

    seats = cursor.fetchall()

    connection.close()

    return {
        "session":
            dict(session),

        "seats": [
            dict(seat)
            for seat in seats
        ]
    }


def get_latest_statistics():
    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            id,
            persons,
            total_seats,
            occupied_seats,
            empty_seats,
            occupancy_rate,
            fps,
            source_type,
            source_name,
            created_at
        FROM analysis_sessions
        ORDER BY id DESC
        LIMIT 1
    """)

    row = cursor.fetchone()

    connection.close()

    if row is None:
        return {
            "id": None,
            "persons": 0,
            "total_seats": 0,
            "occupied_seats": 0,
            "empty_seats": 0,
            "occupancy_rate": 0.0,
            "fps": None,
            "source_type": None,
            "source_name": None,
            "created_at": None
        }

    return dict(row)


if __name__ == "__main__":
    init_database()