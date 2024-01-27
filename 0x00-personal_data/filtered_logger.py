#!/usr/bin/env python3
"""Use regex to replace and obfuscate data"""
import logging
import mysql.connector
import os
import re
from typing import List


class RedactingFormatter(logging.Formatter):
    """ Redacting Formatter class
        """

    REDACTION = "***"
    FORMAT = "[HOLBERTON] %(name)s %(levelname)s %(asctime)-15s: %(message)s"
    SEPARATOR = ";"

    def __init__(self, fields: List[str]):
        super(RedactingFormatter, self).__init__(self.FORMAT)
        self.fields = fields

    def format(self, record: logging.LogRecord) -> str:
        """Returns filtered values from log records"""
        return filter_datum(self.fields, self.REDACTION,
                            super().format(record), self.SEPARATOR)

PII_FIELDS = ("name", "email", "ssn", "password")

def get_db() -> mysql.connector.connection.MySQLConnection:
    """Secure connection to mysql database"""
    db_connect = mysql.connector.connect(
        user = os.getenv('PERSONAL_DATA_DB_USERNAME', 'root'),
        password = os.getenv('PERSONAL_DATA_DB_PASSWORD', ''),
        host=os.getenv('PERSONAL_DATA_DB_HOST', 'localhost'),
        database=os.getenv('PERSONAL_DATA_DB_NAME')
    )
    return db_connect


def filter_datum(fields: List[str], redaction: str, message: str,
                 separator: str) -> str:
    """Return a log message obfuscated using regex"""
    for field in fields:
        message = re.sub(f'{field}=(.*?){separator}',
                         f'{field}={redaction}{separator}', message)
    return message

def get_logger() -> logging.Logger:
    """Logger object with PII_FIELDS"""
    logger = logging.get_logger("user_data")
    logger.setLevel(logging.INFO)
    logger.propagate(false)

    stream_handler = logging.Streamhandler()
    stream_handler.setLevel(loggin.INFO)

    formatter = RedactingFormatter(list(PII_FIELDS))
    stream_handler.set_formatter(formatter)

    logger.add_handler(stream_handler)
    return logger

def main() -> None:
    """Get and display all rows in a database, and log
    them after filtering to hide the PII"""
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT * FROM users;")

    headers = [field[0] for field in cur.description]
    logger = get_logger()

    for row in cur:
        info_answer = ''
        for f, p in zip(row, headers):
            info_answer += f'{p}={(f)}; '
        logger.info(info_answer)

    cur.close()
    db.close()

if __name__ == "__main__":
    main()
