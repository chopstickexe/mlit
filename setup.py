from setuptools import setup, find_packages

setup(
    name="mlit",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "requests",
        "bs4",
        "mcp[cli]>=1.4.0",
    ],
)