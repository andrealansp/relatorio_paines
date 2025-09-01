import os
import time
import traceback
import logging

import psycopg2
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)
logging.basicConfig(
    filename="./bd.log",
    format="%(asctime)s - %(levelname)s: %(message)s",
    encoding="utf-8",
    level=logging.WARNING,
)


class Database:
    def __init__(self):
        self.__con = {
            "dbname": os.getenv("DB_NAME"),
            "user": os.getenv("DB_USER"),
            "password": os.getenv("DB_PASSWORD"),
            "host": os.getenv("DB_HOST"),
            "port": os.getenv("DB_PORT"),
        }

    @property
    def con(self):
        return self.__con

    def registrar_uptime(self, ponto: dict[str, str]) -> bool:
        insert_sql = """INSERT INTO relatorios_painel(data_registro, ponto, ip, status, uptime) 
        VALUES (%s, %s, %s, %s, %s);"""

        try:
            with psycopg2.connect(**self.con) as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        insert_sql,
                        (
                            ponto.get("data_registro", "Sem coleta"),
                            ponto.get("ponto", "Sem coleta"),
                            ponto.get("ip", "Sem coleta"),
                            ponto.get("status", "Sem coleta"),
                            ponto.get("uptime", "Sem coleta"),
                        ),
                    )
                    conn.commit()
                    return True
        except psycopg2.Error as e:
            logger.error("Error inserting user:", e, traceback.format_exc())
            return False
        except Exception as e:
            logger.error("Unexpected error:", e, traceback.format_exc())
            return False

    def get_sites_information(self) -> list[tuple[any,...]]:
        select_sql = """SELECT distinct(ponto), ip FROM cameras WHERE ponto IN (
        'P0091','P0162','P0163','P0165', 'P0166','P0169','P0171','P0174','P0175','P0181',
        'P0187','P0188','P0190','P0192','P0193','P0196','P0197','P0201','P0202','P0203',
        'P0206','P0212','P0213','P0216','P0220','P0221','P0224','P0225','P0229','P0231',
        'P0233','P0234','P0235','P0236','P0239')"""

        try:
            with psycopg2.connect(**self.con) as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        select_sql,
                    )
                    return cur.fetchall()
        except psycopg2.Error as e:
            logger.error("Error inserting user:", e, traceback.format_exc())
            return [('Error', e)]
        except Exception as e:
            logger.error("Unexpected error:", e, traceback.format_exc())
            return [('Error', e)]