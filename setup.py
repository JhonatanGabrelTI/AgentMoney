from setuptools import setup, find_packages

setup(
    name="agentmoney",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "click>=8.1.0",
        "colorama>=0.4.6",
        "rich>=13.0.0",
        "python-dotenv>=1.0.0",
        "pydantic>=2.0.0",
        "schedule>=1.2.0",
    ],
    entry_points={
        "console_scripts": [
            "agentmoney=main:cli",
        ],
    },
    python_requires=">=3.12",
)
