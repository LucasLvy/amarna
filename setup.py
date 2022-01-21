from setuptools import setup, find_packages

setup(
    name="amarna",
    version="0.1",
    description="Amarna is a static-analyzer for the Cairo programming language.",
    author="Trail of Bits",
    license="",
    packages=find_packages(),
    install_requires=[
        "lark",
    ],
    entry_points={
        "console_scripts": [
            "amarna=amarna.command_line:main",
        ],
    },
)