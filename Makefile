all:
	find -name '*.py' | xargs -I file pep8 file  && ./runtests.sh && \
	find -name '*.py' | xargs -I file pylint --reports=n file
