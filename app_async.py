import asyncio
import aiohttp
from netmiko import ConnectHandler
from netmiko import NetMikoTimeoutException, NetMikoAuthenticationException
from datetime import datetime
from db import Database
import logging


# Credenciais (iguais para todos os roteadores, se necessário personalize)
username = 'admin'
password = 'perkons6340'

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG, filename='./app.log', filemode='w', encoding="utf-8",
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

db = Database()
roteadores = db.get_sites_information()
print(roteadores)


logger.info("Script Inicializado")
def registrar_status(ponto, ip, status, uptime=""):
    retorno = db.registrar_uptime({"data_registro":datetime.now().isoformat(),"ponto": ponto, "ip": ip, "status": status, "uptime": uptime})
    if retorno:
        print("Registrado com sucesso!")

for ponto, ip in roteadores:
    print("Ponto: ", ponto)
    print("IP: ", ip)
    device = {
        'device_type': 'mikrotik_routeros',
        'host': ip,
        'username': username,
        'password': password,
        'port': 45162,
        'global_delay_factor': 2,
    }

    try:
        connection = ConnectHandler(**device)

        # Envia o comando completo
        output = connection.send_command("/system resource print")

        # Busca a linha com "uptime"
        uptime = ""
        for line in output.splitlines():
            if "uptime" in line.lower():
                uptime = line.split(":")[-1].strip()
                break

        registrar_status(ponto, ip, "ONLINE", uptime)
        connection.disconnect()

    except (NetMikoTimeoutException, NetMikoAuthenticationException) as e:
        registrar_status(ponto, ip, "OFFLINE")

    logger.info("Script finalizado com sucesso!")