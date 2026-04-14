from setuptools import setup, find_packages

setup(
    name="voria",
    version="0.0.5",
    description="AI-powered CLI tool for open source contributors",
    author="voria Contributors",
    packages=find_packages(),
    python_requires=">=3.9",
    install_requires=[
        "pydantic>=2.0",
        "python-dotenv>=1.0",
        "httpx>=0.24.0",  # Async HTTP client
        "aiofiles>=23.0",  # Async file I/O
    ],
    entry_points={
        "console_scripts": [
            "voria=voria.engine:main",
        ],
    },
)
