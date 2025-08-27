from setuptools import setup, find_packages

setup(
    name="lab_ref",
    version="0.1.0",
    description="Библиотека для работы с референсными значениями лабораторных исследований.",
    author="Ваше Имя",
    author_email="your@email.com",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[],
    python_requires=">=3.7",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
