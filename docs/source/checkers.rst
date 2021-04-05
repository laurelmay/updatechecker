Creating update checkers
========================

Creating an update checker is a fairly straightforward process and can be
accomplished in either of two ways:

* Contributing the checker to the project and placing it in
  :py:mod:`~updatechecker.checkers`
* Decorating the checker with :py:func:`~updatechecker.checkers.register_checker`.

In either case, the update checker must be a subclass of
:py:class:`~updatechecker.checker.BaseUpdateChecker`. There are various fields that
must be specified at a class level and then the ``_load`` method must be implemented
that sets some instance variables.

Every updatechecker has a :py:class:`requests.Session` object available as ``self.session``
that can be used to make HTTP requests. This session is shared across all update checkers
in the application. This session is passed to
:py:meth:`BaseUpdateChecker.__init__ <updatechecker.checker.BaseUpdateChecker>`.

A very basic update checker that could check for the latest version of this software would
be:

.. code-block:: python

   import hashlib

   from updatechecker.checker import BaseUpdateChecker
   from updatechecker.checkers import register_checker

   @register_checker
   class UpdateCheckerUpdateChecker(BaseUpdateChecker):
       # Set the required class variables
       short_name = "updatechecker"
       name = "updatechecker"

       def _load(self):
           releases_api = "https://api.github.com/repos/kylelaker/updatechecker/releases/latest"
           headers = {'Accept': "application/vnd.github.v3+json"}
           # Get the information for the latest release
           latest_release_data = self.session.get(releases_api, headers=headers).json()
           latest_release_url = latest_release_data["tarball_url"]
           latest_release_version = latest_release_data["version"].lstrip("v")

           # No API to get the hash is available so we have to calculate it ourselves
           download_response = self.session.get(latest_release_url)
           sha1_hash = hashlib.sha1(download_response.content).hexdigest()

           # Set the required instance attributes
           self._latest_url = latest_release_url
           self._latest_version = latest_release_version
           self._sha1_hash = sha1_hash

So, setting ``_latest_url``, ``_latest_version``, and ``_sha1_hash`` within ``_load`` is
all that's required to have the information on the latest available version. In general
consumers of this library should be expecting that ``_load`` will be a slower operation.

It is also always preferable to get information on an expected SHA1 hash from the upstream
source rather than downloading the file and calculating it yourself; however, in some cases
such as GitHub releases, that may not always be an option. For an example of an update checker
that is able to fetch the hash, see the source code for the `Eclipse Update Checker`_.

.. _Eclipse Update Checker: https://github.com/kylelaker/updatechecker/blob/main/updatechecker/checkers/eclipse_java.py