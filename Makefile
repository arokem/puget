test:
	py.test --pyargs puget --cov-report term-missing --cov=puget

flake8:
	flake8 --ignore N802,N806 `find . -name \*.py | grep -v setup.py | grep -v version.py | grep -v __init__.py | grep -v /doc/`

