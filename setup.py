from setuptools import setup, find_packages

setup(
    name="chatscanner",
    version="0.1.0",
    description="A CLI tool and library to scan websites for chatbots.",
    author="Paolo Di Prodi",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "click>=8.0",
        "requests",
        "beautifulsoup4",
        "playwright"
    ],
    python_requires=">=3.7",
    entry_points={
        "console_scripts": [
            "chatscanner=chatscanner.cli:main"
        ]
    },
)
