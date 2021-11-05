import pathlib

from setuptools import setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

# This call to setup() does all the work
setup(
    name="simplify-rest-framework",
    version="0.11.0",
    description="Simplified version of django rest framework",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/mahbd/simplify-rest-framework",
    author="Mahmudul Alam",
    author_email="mahmudula2000@gmail.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        'Operating System :: OS Independent',
        'Environment :: Web Environment',
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        'Framework :: Django',
        'Framework :: Django :: 4.0',
    ],
    packages=['simplify_rest_framework'],
    include_package_data=True,
    install_requires=["django >= 3.2.0"],
)
