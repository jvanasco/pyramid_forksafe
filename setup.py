"""pyramid_forksafe installation script.
"""
import os
import re

from setuptools import setup
from setuptools import find_packages

HERE = os.path.abspath(os.path.dirname(__file__))

long_description = (
    description
) = "Standardizes server `fork` events into Pyrmamid events"
with open(os.path.join(HERE, "README.md")) as r_file:
    long_description = r_file.read()

# store version in the init.py
with open(os.path.join(HERE, "pyramid_forksafe", "__init__.py")) as v_file:
    VERSION = re.compile(r'.*__VERSION__ = "(.*?)"', re.S).match(v_file.read()).group(1)


requires = [
    "pyramid",
    "zope.interface",  # should be in pyramid
]
tests_require = [
    "pytest",
    "pyramid_debugtoolbar",
]
testing_extras = tests_require + []


setup(
    name="pyramid_forksafe",
    version=VERSION,
    url="https://github.com/jvanasco/pyramid_forksafe",
    author="Jonathan Vanasco",
    author_email="jonathan@findmeon.com",
    description=description,
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        "Intended Audience :: Developers",
        "Framework :: Pyramid",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
    keywords="web pyramid fork uwsgi nginx",
    license="MIT",
    packages=find_packages(exclude=("tests",)),
    include_package_data=True,
    zip_safe=False,
    install_requires=requires,
    tests_require=requires,
    extras_require={
        "testing": testing_extras,
    },
    test_suite="tests",
)
