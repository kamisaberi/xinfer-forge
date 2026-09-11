from setuptools import setup, find_packages

setup(
    name="xinfer-forge",
    version="1.0.0",
    description="Autonomous On-Device Model Adaptation & Continuous Learning Engine",
    author="Kamran Saberifard",
    author_email="kamran@blackbox-sentinel.io",
    packages=find_packages(),
    python_requires=">=3.10",
    install_requires=[
        "torch>=2.0.0",
        "torchvision>=0.15.0",
        "onnx>=1.14.0",
        "onnxruntime>=1.15.0",
        "numpy>=1.23.0",
        "pyyaml>=6.0",
        "requests>=2.28.0",
        "scikit-learn>=1.2.0",
    ],
    entry_points={
        "console_scripts": [
            "forge-cli=forge.cli:main",
        ],
    },
)