from setuptools import setup

setup(
    name="andi-py",
    version="1.2.0",
    description="Analog Discovery 2 python API",
    long_description="file: README.md",
    author="Florian Kolbl - Yannick Bornat - Louis Regnacq",
    packages=["andi"],  # same as name
    include_package_data=True,
    url="https://github.com/fkolbl/andi",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    install_requires=["numpy"],  # external packages as dependencies
    python_requires=">=3.6",
)
