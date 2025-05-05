from setuptools import setup, find_packages

setup(
    name="simulacra",
    version="2.0.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.10",
    install_requires=[
        "colorama",
        "orjson",
        "msgpack",
        "zstandard"
    ],
    extras_require={
        "dev": [
            "pytest>=7.0",
            "pytest-asyncio",
            "pytest-benchmark",
            "pytest-cov",
            "black",
            "mypy"
        ]
    }
)
