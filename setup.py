import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="PyHoot",
    version="1.0.1",
    author="Nexity",
    author_email="o7fireincorporated@gmail.com",
    description="A python package to interact with Kahoot!",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/o7-Fire/KahootPY/",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    keywords=["kahoot","bot"],
    install_requires=["websockets","pymitter","requests","user_agent"],
)
