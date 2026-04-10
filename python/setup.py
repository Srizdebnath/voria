from setuptools import setup, find_packages

setup(
    name="victory",
    version="0.1.0",
    description="AI-powered CLI tool for open source contributors",
    author="Victory Contributors",
    packages=find_packages(),
    python_requires=">=3.9",
    install_requires=[
        "pydantic>=2.0",
        "python-dotenv>=1.0",
    ],
    entry_points={
        "console_scripts": [
            "victory=victory.engine:main",
        ],
    },
)
