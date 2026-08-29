from setuptools import setup, find_packages

setup(
    name="nancy",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "click",
        "requests",
        "python-dotenv",
        "openai",
    ],
    entry_points={
        "console_scripts": [
            "nancy = nancy.cli:cli",
        ],
    },
)