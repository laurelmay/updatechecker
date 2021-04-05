updatechecker Documentation
===========================

``updatechecker`` is a Python library to support checking for updates to software.
The classes that handle update checking are called "checkers" and return the version
number, download URL, and SHA1 hash of the latest version.

For an example of creating an API around this code and providing notifications when
updates to watched software are available, see the |updatechecker-infra|_ project which
uses AWS Chalice and the AWS CDK.

.. |updatechecker-infra| replace:: ``updatechecker-infra``
.. _updatechecker-infra: https://github.com/kylelaker/updatechecker-infra

.. toctree::
   :hidden:
   :maxdepth: 2
   :caption: Contents:

   checkers
   modules


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
