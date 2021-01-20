.venv:
	virtualenv --python=python3 .venv
	.venv/bin/pip install -e '.[dev]'

test: .venv
	.venv/bin/pytest

publish:
	rm -rf dist/
	python setup.py sdist bdist_wheel
	twine upload dist/*
