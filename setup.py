from setuptools import setup, find_packages

setup(
    name="nancy",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "click",
        "rich",
        "python-dotenv",
        "requests",
        "openai",
    ],
    entry_points={
        "console_scripts": [
            "nancy = nancy.cli:cli",
        ],
    },
    python_requires=">=3.11",
    description="CLI-агент для генерации автотестов с помощью LLM",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/Wolffather/nancy",
    author="Мирсков Савелий",
    author_email="smirskov93@gmail.com",
)