
# C:\Scripts\Deep Blue scripts and files\pool_controller\setup.py
from setuptools import setup, find_packages

setup(
    name="pool_controller",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "cryptography",
    ],
)

