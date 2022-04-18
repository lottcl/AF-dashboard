import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()


setuptools.setup(
    name="AF_dashboard",
    version="0.0.1",
    author="Catie Lott",
    author_email="catie.lott@emory.edu",
    description="AF Score Dashboard",
    url="https://github.com/lottcl/AF_dashboard",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=[
                      'pandas',
                      'numpy',
                      'datetime',
                      'dash >=1.20',
                      'waitress',
                      'dash_bootstrap_components',
                      'dash_bootstrap_templates',
                      'plotly',
                      'statsmodels'
                      ],
    zip_safe=False
)