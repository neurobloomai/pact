import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pact-protocol",
    version="0.1.0",
    author="Neurobloom.ai",
    author_email="team@neurobloom.ai",
    description="PACT: Protocol for Agent Collaboration & Transfer",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/neurobloomai/pact",
    project_urls={
        "Documentation": "https://github.com/neurobloomai/pact#readme",
        "Source": "https://github.com/neurobloomai/pact",
        "Tracker": "https://github.com/neurobloomai/pact/issues",
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    package_dir={"": "pact_protocol"},
    packages=setuptools.find_packages(where="pact_protocol"),
    python_requires=">=3.8",
    install_requires=[
        "fastapi>=0.95.0",
        "uvicorn>=0.20.0",
        "pydantic>=1.10.0",
        "typing-extensions>=4.0.0"
    ],
    include_package_data=True,
    zip_safe=False,
)
