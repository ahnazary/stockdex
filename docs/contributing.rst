Contributing
============

Stockdex is open source, and contributions of any kind are welcome: bug
reports, ideas, documentation and code.

How to contribute
-----------------

- **Issues**: found a bug or have an idea? Open an
  `issue <https://github.com/ahnazary/stockdex/issues>`_ and describe it.
- **Discussions**: not sure about an idea yet? Start a thread in the
  repository's *Discussions* tab.
- **Pull requests**: fork the repository and open a PR with a short
  description of the change and any related issues.

Development setup
-----------------

.. code-block:: bash

   git clone https://github.com/ahnazary/stockdex.git
   cd stockdex
   pip install -r requirements.txt -r requirements_tests.txt
   pytest -q

Tests marked ``live`` are skipped by default; run them with
``pytest --run-live``. Some older tests are not marked yet and still call
external websites (for example the Finviz, Digrin and Macrotrends interface
tests), so ``pytest -q`` needs a network connection and can hit rate limits.
For an offline run, use the fixture-based suites:

.. code-block:: bash

   pytest -q tests/claude tests/test_yahoo_web_deprecated.py

Code style
----------

The code is formatted with ``black`` and ``isort --profile black`` and
checked with ``ruff``.

Building the docs
-----------------

.. code-block:: bash

   pip install -r requirements.txt -r requirements_sphinx.txt
   sphinx-build -b html docs docs/build

The docs are rebuilt and published on every merge to ``main``.

.. centered:: Thank you for contributing!
