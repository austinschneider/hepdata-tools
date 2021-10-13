from setuptools import setup


def readme():
    with open("README.md") as f:
        return f.read()


setup(
    name="hepdata_tools",
    version="0.0.0",
    description="Simple tools for creating a hepdata.net release..",
    long_description=readme(),
    url="https://github.com/austinschneider/hepdata-tools",
    author="Austin Schneider",
    author_email="austin.schneider@icecube.wisc.edu",
    license="LGPL-3.0",
    packages=["hepdata_tools",
        "hepdata_tools.text",
        "hepdata_tools.types"],
    install_requires=[
        "numpy",
        "scipy",
    ],
    zip_safe=True,
)
