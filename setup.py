from distutils.core import setup
from setuptools import find_packages
import aio_api_ros
VERSION = aio_api_ros.version

setup(
    name='aio_api_ros',
    version=VERSION,
    packages=find_packages(),
    url='https://github.com/frostspb/aio_api_ros',
    license='MIT',
    author='Frostspb',
    description='async implementation Mikrotik api',
    long_description="""Only Python 3.5+""",
    keywords=["mikrotik", "asyncio", "apiRos"],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python :: 3.5",
    ],
    install_requires=[

    ],
)
