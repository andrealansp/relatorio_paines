# Nome do arquivo: main_script.py

import asyncio
import logging
import os
from datetime import datetime

import asyncpg
from dotenv import load_dotenv
from netmiko import Netmiko
from netmiko.exceptions import (NetmikoAuthenticationException,
                                NetmikoTimeoutException)
import traceback

# Importa as funções do seu módulo de banco de dados
from db_async import get_site_informations, registrar_uptime

# --- Configuração Inicial ---
load_dotenv()  # Carrega as variáveis do arquivo .env

# Configuração do Logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, filename='./app.log', filemode='w', encoding="utf-8",
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Credenciais dos roteadores
USERNAME = 'admin'
PASSWORD = 'perkons6340'

# Configurações do Banco de Dados (lidas do .env)
DB_CONFIG = {
    'user': os.getenv("DB_USER"),  # Renomeado para evitar conflito com usuário do sistema
    'password': os.getenv("DB_PASSWORD"),
    'database': os.getenv("DB_NAME"),
    'host': os.getenv("DB_HOST"),
    'port': os.getenv("DB_PORT")
}


# --- FUNÇÃO CORRIGIDA ---
async def check_router_status(pool, ponto, ip):
    """
    Conecta a um único roteador, verifica seu status e registra no banco de dados.
    Usa o padrão try...finally para garantir a desconexão.
    """
    device = {
        'device_type': 'mikrotik_routeros',
        'host': str(ip),
        'username': USERNAME,
        'password': PASSWORD,
        'port': 45162,
        'global_delay_factor': 2,
        'banner_timeout': 20,
    }

    status_data = {
        "data_registro": datetime.now().isoformat(),
        "ponto": ponto,
        "ip": ip,
        "status": "OFFLINE",
        "uptime": ""
    }

    connection = None  # 1. Inicializa a variável de conexão como None
    try:
        # 2. A criação do objeto é síncrona, a conexão real ocorre no primeiro 'await'
        connection = Netmiko(**device)

        # O primeiro comando 'await' efetivamente estabelece a conexão
        output = await connection.send_command("/system resource print")

        uptime_value = ""
        for line in output.splitlines():
            if "uptime" in line.lower():
                uptime_value = line.split(":", 1)[-1].strip()
                break

        status_data["status"] = "ONLINE"
        status_data["uptime"] = uptime_value
        logger.info(f"Sucesso: {ponto} ({ip}) - Status: ONLINE, Uptime: {uptime_value}")

    except (NetmikoTimeoutException, NetmikoAuthenticationException) as e:
        logger.error(f"Falha de conexão em {ponto} ({ip}): {e}")
    except Exception as e:
        logger.critical(f"Erro inesperado em {ponto} ({ip}): {e}")
    finally:
        # 3. O bloco 'finally' garante que a desconexão sempre seja tentada
        if connection:
            await connection.disconnect()

    # Registra o resultado (ONLINE ou OFFLINE) no banco de dados
    await registrar_uptime(pool, status_data)


async def main():
    """
    Função principal que cria o pool de conexões e orquestra as tarefas.
    """
    logger.info("Script Inicializado")
    pool = None  # Garante que a variável pool exista
    try:
        # Cria o pool de conexões com o banco de dados
        async with asyncpg.create_pool(**DB_CONFIG) as pool:
            logger.info("Pool de conexões com o banco de dados criado com sucesso.")

            # Busca as informações dos roteadores usando o pool
            roteadores = await get_site_informations(pool)
            logger.info(f"Encontrados {len(roteadores)} roteadores para verificação.")

            # Cria uma lista de tarefas, passando o pool para cada uma
            tasks = [check_router_status(pool, ponto, ip) for ponto, ip in roteadores]

            # Executa todas as tarefas concorrentemente
            await asyncio.gather(*tasks)

    except Exception as e:
        logger.critical(f"Ocorreu um erro fatal na execução principal: {e}")
        print(traceback.format_exc())
    finally:
        logger.info("Script finalizado com sucesso!")


if __name__ == "__main__":
    asyncio.run(main())