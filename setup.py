"""
Setup script for raincloudpy package.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the contents of README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

setup(
    name="raincloudpy",
    version="0.4.4",
    author="bsgarcia",
    author_email="basilegarcia@gmail.com",
    description="Beautiful raincloud plots for Python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/bsgarcia/raincloudpy",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Visualization",
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
    install_requires=[
        "numpy>=1.19.0",
        "matplotlib>=3.3.0",
        "scipy>=1.5.0",
        "pandas>=1.1.0",
        "seaborn>=0.11.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=22.0",
            "flake8>=3.9",
            "mypy>=0.9",
        ],
    },
    keywords="visualization raincloud plots statistics data-science",
    project_urls={
        "Bug Reports": "https://github.com/bsgarcia/raincloudpy/issues",
        "Source": "https://github.com/bsgarcia/raincloudpy",
        "Documentation": "https://github.com/bsgarcia/raincloudpy#readme",
    },
)
