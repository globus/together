from setuptools import setup

setup(
    name="together-subsample",
    install_requires="together",
    entry_points={"together": ["subsample = together_subsample"]},
    py_modules=["together_subsample"],
)
