from setuptools import setup, find_packages

setup(
    name='stockdex',
    version='0.1.2',
    packages=find_packages(),
    install_requires=[
        'pandas==2.0.3',
        'beautifulsoup4==4.12.2'
    ],
    python_requires='>=3.8',
    author='Amir Nazary',
    description='A package to get stock data from Yahoo Finance',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/ahnazary/stockdex',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)
