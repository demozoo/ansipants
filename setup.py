from setuptools import setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="ansipants",
    version="0.1.2",
    packages=["ansipants"],
    url='https://github.com/demozoo/ansipants/',
    author="Matt Westcott",
    author_email="matthew@west.co.tt",
    description="Convert ANSI art to HTML",
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Topic :: Multimedia :: Graphics :: Graphics Conversion",
        "Topic :: Text Processing :: Markup :: HTML",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    license="BSD",
)
