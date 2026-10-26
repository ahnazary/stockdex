from pathlib import Path

from setuptools import find_packages, setup

try:
    from __version__ import VERSION
except ModuleNotFoundError as error:
    if error.name != "__version__":
        raise
    # Release automation writes __version__.py; source checkouts need a version too.
    VERSION = "0.0.0+local"

ROOT = Path(__file__).resolve().parent

setup(
    name="stockdex",
    version=VERSION,
    packages=find_packages(),
    install_requires=(ROOT / "requirements.txt")
    .read_text(encoding="utf-8")
    .splitlines(),
    extras_require={"mcp": ["mcp>=2.3,<3"]},
    entry_points={
        "console_scripts": [
            "stockdex-claude=stockdex.claude_cli:main",
            "stockdex-mcp=stockdex.claude_mcp:main",
        ]
    },
    python_requires=">=3.9",
    author="Amir Nazary",
    author_email="ah.nazary.aghchemazary@gmail.com",
    description="A package to get stock data from Yahoo Finance",
    long_description=(ROOT / "README.md").read_text(encoding="utf-8"),
    long_description_content_type="text/markdown",
    url="https://github.com/ahnazary/stockdex",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_data={"stockdex": ["chromedriver_linux64/*"]},
)
