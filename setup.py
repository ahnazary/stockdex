from __version__ import VERSION
from setuptools import find_packages, setup

setup(
    name="stockdex",
    version=VERSION,
    packages=find_packages(),
    install_requires=open("requirements.txt").read().splitlines(),
    python_requires=">=3.8",
    author="Amir Nazary",
    description="A package to get stock data from Yahoo Finance",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/ahnazary/stockdex",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_data={"stockdex": ["chromedriver_linux64/*"]},
)
