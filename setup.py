from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="streamdeck-canvas-renderer",
    version="0.1.0",
    author="Jules Mellot",
    author_email="jules@tllm.fr",
    description="A real-time canvas renderer for Elgato Stream Deck",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/julesmellot/streamdeck-canvas-renderer",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Multimedia :: Graphics",
        "License :: Other/Proprietary License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "Pillow>=10.0.0",
        "streamdeck>=0.9.0",
        "numpy>=1.24.0",
    ],
)