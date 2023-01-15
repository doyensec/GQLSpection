from setuptools import setup, find_packages
import os

pwd = os.path.abspath(os.path.dirname(__file__))
readme_path = os.path.join(pwd, "README.md")

with open(readme_path) as f:
    readme = f.read()

setup(
    name="gqlspection",
    version="0.0.1a1",
    description="GraphQL Introspection parsing and query generation",
    long_description=readme,
    long_description_content_type="text/markdown",
    url="https://github.com/doyensec/gqlspection",
    author="Andrew Konstantinov",
    author_email="andrew@doyensec.com",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "Intended Audience :: System Administrators",
        "Environment :: Console",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 2 :: Only",
        "License :: OSI Approved :: Apache Software License",
        "Topic :: Software Development :: Code Generators",
        "Topic :: Security"
    ],
    keywords="graphql, introspection",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires="~=2.7",
    extras_require={
        "web": ["requests"],
        "test": ["build", "pathlib2", "pytest", "twine"]
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