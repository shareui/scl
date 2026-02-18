from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="structcfg-parser",
    version="1.2.0",
    author="shareui",
    description="Parser for Structured Configuration Language (SCL)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/shareui/scl",
    packages=find_packages(),
    classifiers=[
        'Development Status :: 4 - Beta',
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.7",
    keywords="parser, configuration, scl, config, structured-config",
    project_urls={
        "Bug Reports": "https://github.com/shareui/scl/issues",
        "Source": "https://github.com/shareui/scl",
    },
)