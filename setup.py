#!/user/bin/env python
from setuptools import setup, find_packages

setup(
    name="axosoft_api",
    version="0.1.0",
    description="An Axosoft API Client",
    license="MIT",
    install_requires=["requests", "nose"],
    author="Clifton Kaznocha",
    author_email="clifton@kaznocha.com",
    url="http://github.com/ckaznocha/axosoft-python",
    packages=find_packages(),
    keywords="Axosoft"
)