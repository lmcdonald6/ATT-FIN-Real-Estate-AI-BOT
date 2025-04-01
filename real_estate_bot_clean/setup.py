"""
Real Estate AI Bot
Installation configuration.
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="real-estate-ai-bot",
    version="1.0.0",
    author="Lewis McDaniel",
    description="An intelligent real estate analysis bot with lead scoring and property insights",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/real-estate-ai-bot",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Real Estate Professionals",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Office/Business :: Real Estate",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "rebot=src.run_bot:main",
        ],
    },
)
