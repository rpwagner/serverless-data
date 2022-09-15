import os
from setuptools import setup, find_packages

version_ns = {}
with open(os.path.join("serverless_data", "version.py")) as f:
    exec(f.read(), version_ns)
version = version_ns["__version__"]

setup(
    name="serverless-data",
    version=version,
    packages=find_packages(),
    description="Serverless Data Research Repository",
    long_description=(
        "The Serverless Data Research Repository is an example of how to \
        host research data using existing services."
    ),
    install_requires=['globus_sdk',
                          'pytablewriter'],
    python_requires=">=3.10.1",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: BSD License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Topic :: Database"
    ],
    keywords=[
        "datacite",
        "repository",
        "catalog",
        "collection",
        "metadata",
    ],
    license="BSD License",
    url="https://rpwagner.github.io/serverless-data/",
)
