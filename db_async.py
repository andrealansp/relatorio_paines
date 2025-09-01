# Nome do arquivo: db_async.py

import logging
from datetime import datetime

import asyncpg

logger = logging.getLogger(__name__)


# A configuração do logging e do dotenv é melhor centralizada no script principal.

async def get_site_informations(pool):
    """
    Busca a lista de roteadores do banco de dados usando uma conexão do pool.
    """
    # Usar 'async with' garante que a conexão seja devolvida ao pool.
    async with pool.acquire() as conn:
        # A query original está mantida.
        values = await conn.fetch(
            """SELECT distinct(ponto), ip FROM cameras WHERE ponto IN (
            'P0091', 'P0162', 'P0163', 'P0165', 'P0166', 'P0169', 'P0171', 'P0174', 'P0175', 'P0181',
            'P0187', 'P0188', 'P0190', 'P0192', 'P0193', 'P0196', 'P0197', 'P0201', 'P0202', 'P0203',
            'P0206', 'P0212', 'P0213', 'P0216', 'P0220', 'P0221', 'P0224', 'P0225', 'P0229', 'P0231',
            'P0233', 'P0234', 'P0235', 'P0236', 'P0239')"""
        )
        return values


async def registrar_uptime(pool, data):
    """
    Registra o status de um roteador no banco de dados usando uma conexão do pool.

    Args:
        pool: O pool de conexões asyncpg.
        data (dict): Um dicionário contendo as informações a serem inseridas.
    """
    # Acessa o pool para pegar uma conexão disponível
    async with pool.acquire() as conn:
        # CORREÇÃO: asyncpg usa $1, $2, etc. para parâmetros
        await conn.execute(
            """INSERT INTO relatorios_painel(data_registro, ponto, ip, status, uptime) 
               VALUES ($1, $2, $3, $4, $5)""",
            data.get('data_registro'),
            data.get('ponto'),
            data.get('ip'),
            data.get('status'),
            data.get('uptime')
        )