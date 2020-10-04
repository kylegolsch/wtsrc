import sys
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="wtsrc",
    version="1.3.0",
    author="Kyle Golsch",
    author_email="kyle@sagelab.com",
    description="For automating some manual processes with wtsrc",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.5',
    entry_points="""
       [console_scripts]
       wtsrc = wtsrc:run
    """
)
