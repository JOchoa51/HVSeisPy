from setuptools import setup, find_packages

setup(
    name="hvseispy",  # Package name
    version="1.0",  # Version number
    author="Jesús Ochoa",
    author_email="ochoacontrerasjesus8@gmail.com",
    description="HVSeisPy calculates HV spectral ratio from 3-channel acceleration data, as well as various signal analysis operations.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/JOchoa51/HVSeisPy",  # GitHub or project URL
    packages=find_packages(),  # Automatically find package directories
    classifiers=[  # Metadata for PyPI
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",  # Minimum Python version
    install_requires=[  # Dependencies
        "numpy",
        "scipy",
        "obspy",
        "matplotlib",
        "pykooh"
    ],
)
