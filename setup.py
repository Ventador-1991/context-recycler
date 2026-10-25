from setuptools import setup, find_packages

setup(
    name="context-recycler",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "tiktoken>=0.7.0"
    ],
    entry_points={
        "console_scripts": [
            "context-recycler=context_recycler.cli:main"
        ]
    }
)
