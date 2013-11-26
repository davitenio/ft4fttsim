all:
	find -name '*.py' | xargs -I file pep8 file  && ./runtests.sh && \
	pylint --reports=n ft4fttsim/*.py
