from setuptools import setup

setup(
    name="together-sample",
    install_requires="together",
    entry_points={"together": ["root = together_sample"]},
    py_modules=["together_sample"],
)
