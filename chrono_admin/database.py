"""
Připojení k SQLite databázi CHRONO
"""

import pymysql


def get_connection():
    """Vrátí připojení k MySQL databázi."""
    return pymysql.connect(
        host="dbs.spskladno.cz",
        user="student13",
        password="spsnet",
        database="vyuka13",
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor
    )
