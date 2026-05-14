from setuptools import setup, find_packages

setup(
    name="ghost-framework",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "playwright",
        "pytest",
        "httpx",
        "portalocker",
        "axios"
    ],
    description="Universal AI Self-Healing Automation Framework (Ghost Mode)",
    author="HealQA Team",
)
