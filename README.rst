Update Checker
==============

A framework for checking for updates for various software. Currently supported are:

* `Eclipse IDE for Java Developers`_
* jGRASP_
* `Finch Robot 1 Python`_

.. _Eclipse IDE for Java Developers: https://www.eclipse.org/downloads/packages/release/2021-03/r/eclipse-ide-java-developers
.. _jGRASP: https://www.jgrasp.org
.. _Finch Robot 1 Python: https://www.birdbraintechnologies.com/finch1/python/install/

Adding Checkers
---------------

Add your new update checker to the ``updatechecker/checkers/`` folder. Each checker should
specialize ``checker.BaseUpdateChecker`` and define the following two attributes at the class
level:

* ``name``: The full, friendly, name for the application
* ``short_name``: A unique identifier for the application

Next, define a method, ``_load`` that can set the following attributes on ``self``:

* ``_latest_url``: The full URI where the latest version can be downloaded
* ``_latest_version``: The string for the latest version
* ``_sha1_hash``: The SHA1 hash of the latest version's download

Make sure to take ``self.beta`` in to account when determining the latest version.


Deploying
---------

See the coming `updatechecker-infra`_ repository which provides an example of how to deploy this
application on AWS Lambda using the Chalice framework and CDK. To provide an API of latest 
version information.

.. _updatechecker-infra: https://github.com/kylelaker/updatechecker-infra

