FT4FTTsim is a simulator whose development is being used to design and evaluate
the FT4FTT architecture.


Requirements
============

FT4FTTsim is written in Python 3 and uses the [SimPy 3][simpy] process-based discrete-event simulation library.

For automated testing of the code [pytest][pytest] is used.

[simpy]: http://simpy.readthedocs.org/
[pytest]: http://pytest.org/

Probably the easiest way to install recent versions of both SimPy and pytest is using the `pip` tool. On an Ubuntu machine it should suffice to execute the following commands:

```
sudo aptitude install python3-pip
sudo pip3 install -U pytest
sudo pip3 install -U simpy
```

Coding style
===========

The code is written following the [PEP8][pep8] style guide for Python code. Compliance with PEP8 can be checked using the `pep8` tool, which on Ubuntu can be installed by simply typing `sudo aptitude install pep8`.

[pep8]: http://www.python.org/dev/peps/pep-0008/


Hacking
=======

If you modify the code, please run the Makefile at the root directory of the FT4FTTsim project before considering to commit into the git repository. This will invoke both `pep8` and the `runtests.sh` script, which then invokes `py.test`. If the code does not comply with PEP8, or some test fails, please fix the code and only then proceed with the git commit.
