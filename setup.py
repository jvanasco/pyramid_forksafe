"""pyramid_forksafe installation script.
"""
import os
import re

from setuptools import setup
from setuptools import find_packages

try:
    here = os.path.abspath(os.path.dirname(__file__))
    README = open(os.path.join(here, "README.md")).read()
    README = README.split("\n\n", 1)[0] + "\n"
except:
    README = ""

# store version in the init.py
with open(
    os.path.join(os.path.dirname(__file__), "pyramid_forksafe", "__init__.py")
) as v_file:
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
    description="provides for a unified fork events",
    long_description=README,
    classifiers=[
        "Intended Audience :: Developers",
        "Framework :: Pyramid",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
    keywords="web pyramid fork",
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
