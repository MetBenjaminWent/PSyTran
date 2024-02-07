.. (C) Crown Copyright, Met Office. All rights reserved.

   This file is part of PSyACC and is released under the BSD 3-Clause license.
   See LICENSE in the root of the repository for full licensing details.

Welcome to PSyACC's documentation!
==================================

PSyACC is a Python package for streamlining OpenACC GPU porting efforts using the
`PSyclone <https://github.com/stfc/PSyclone>`__ domain-specific compiler and code
transformation tool.

Before getting started with PSyACC, it is recommended that you familiarise yourself
with the following background material:

* `OpenACC website <https://www.openacc.org>`__.
* `PSyclone documentation <https://psyclone.readthedocs.io/en/stable>`__.

API documentation
-----------------

The API documentation page shows the objects comprising PSyACC.

.. toctree::
    :maxdepth: 1

    API documentation <psyacc>

Alternatively, an alphabetical list can be found on the :ref:`index <genindex>` page.
A :ref:`search engine <search>` is also provided.

Demos
-----

.. toctree::
    :maxdepth: 1

    1. Basic usage <demos/01_psyclone.py>
    2. Inserting kernels directives <demos/02_kernels.py>
    3. Inserting loop directives <demos/03_loop.py>
