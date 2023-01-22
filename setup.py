# coding: utf-8
from __future__ import unicode_literals
from setuptools import setup, find_packages
import os

pwd = os.path.abspath(os.path.dirname(__file__))
readme_path = os.path.join(pwd, "README.md")

with open(readme_path) as f:
    readme = f.read()


def is_jython():
    from platform import python_implementation
    return python_implementation() == 'Jython'


if is_jython():
    # Create _version.py ahead of type by running:
    #   python3 -c "import setuptools_scm; setuptools_scm.get_version(write_to='_version.py')"
    from _version import version

setup(
    name="gqlspection",
    # If Jython, import version from version.py file (should be created ahead of time)
    version=version if is_jython() else None,
    # Otherwise, load version from git tags
    setup_requires=[
        "setuptools_scm"
    ] if not is_jython() else [],
    use_scm_version=not is_jython(),
    description="GraphQL Introspection parsing and query generation",
    long_description=readme,
    long_description_content_type="text/markdown",
    url="https://github.com/doyensec/gqlspection",
    author="Andrew Konstantinov",
    author_email="andrew@doyensec.com",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "Intended Audience :: System Administrators",
        "Environment :: Console",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: Jython",
        "License :: OSI Approved :: Apache Software License",
        "Topic :: Software Development :: Code Generators",
        "Topic :: Security"
    ],
    keywords="graphql, introspection",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=2.7",
    install_requires=[
        "pathlib2; python_version == '2.7'",
        "future;   python_version == '2.7'"
    ],
    extras_require={
        "cli": ["click", "requests"]
    },
    entry_points={
        "console_scripts": [
            "gqlspection=gqlspection:cli"
        ]
    },
    project_urls={
        "Source": "https://github.com/doyensec/gqlspection",
        "Bug Reports": "https://github.com/doyensec/gqlspection/issues",
        "Doyensec Research": "https://www.doyensec.com/research.html"
    }
)
