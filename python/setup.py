from setuptools import setup, find_packages

setup(
    name="victory",
    version="1.0.0",
    description="AI-powered CLI tool for open source contributors",
    author="Victory Contributors",
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
            "victory=victory.engine:main",
        ],
    },
)
