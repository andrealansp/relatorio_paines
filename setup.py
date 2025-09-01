from cx_Freeze import setup, Executable

import os

CAMINHO_PARA_BINARIOS = os.path.join(os.path.dirname(__file__), "venv")

build_exe_options = {
    "packages": ["os","psycopg2","netmiko"],
    "excludes": ["tkinter"],
    "bin_path_includes":
        [
            CAMINHO_PARA_BINARIOS,
    ]
}
base = None
setup(
    name="GetDataMikrotik",
    version="1.0.0",
    description="Software to get a uptime from routers",
    options={"build_exe": build_exe_options},
    executables=[Executable("app.py",base=base)],
)