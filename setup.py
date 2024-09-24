import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="KahootConnect",
    version="0.2.6",
    author="HackySoft",
    author_email="andrexyt@proton.me",
    description="A python package to interact with Kahoot!",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/HackySoftOfficial/KahootConnect",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    keywords=["kahoot","bot","spam"],
    install_requires=["websockets","httpx","asyncio"],
)
