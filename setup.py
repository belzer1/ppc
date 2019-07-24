import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="purephotonicscontrol",
    version="0.0.2",
    author="Matthew Berrington",
    author_email="berrington95@gmail.com",
    description="A package to control PurePhotonics lasers",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://bitbucket.org/matthewberrington/purephotonicscontrol",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
