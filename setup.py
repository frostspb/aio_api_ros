import aio_api_ros
from distutils.core import setup
from setuptools import find_packages

VERSION = aio_api_ros.version

setup(
    name='aio_api_ros',
    version=VERSION,
    packages=find_packages(),
    url='https://github.com/frostspb/aio_api_ros',
    license='MIT',
    author='Frostspb',
    description='async implementation Mikrotik api',
    long_description="""async implementation Mikrotik api
    Only Python 3.5+""",
    keywords=["mikrotik", "asyncio", "apiRos"],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
    install_requires=[

    ],
)
