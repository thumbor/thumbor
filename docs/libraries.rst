Libraries
=========

Even though the process of generating safe image URLs is explained in
the :doc:`security` page, we'll try to provide libraries in each
programming language to ease this process.

Available Libraries
-------------------

Python
~~~~~~

-  `libthumbor <https://github.com/heynemann/libthumbor>`__ - Python's
   extensions to thumbor. These are used to generate safe urls among
   others.
-  `django-thumbor <https://github.com/ricobl/django-thumbor>`__ - A
   django app with templatetags for resizing images with thumbor (by
   `ricobl <https://github.com/ricobl>`__).
-  `django-thumborstorage <https://github.com/Starou/django-thumborstorage>`__
   - A Django custom storage for Thumbor backend (by `Stanislas
   Guerra <https://github.com/Starou>`__).

Node.js
~~~~~~~

-  `thumbor-client <https://github.com/azabroflovski/thumbor-client>`__
    - Thumbor client for Node.js and Browser, SSR friendly
    (by `azabroflovski <https://github.com/azabroflovski>`__).
-  `ThumborJS <https://github.com/rafaelcaricio/ThumborJS>`__ -
   Javascript's extension to thumbor. These are used to generate safe
   urls, encrypted urls among others (by `Rafael
   Carício <https://github.com/rafaelcaricio>`__).
-  `ThumborUrlBuilder <https://github.com/dcaramelo/ThumborUrlBuilder>`__
   - Thumbor client for Node JS (by `David
   Caramelo <https://github.com/dcaramelo>`__).
-  `thumbor <https://github.com/policymic/thumbor>`__ - Thumbor client
   for Node JS (by `PolicyMic <https://github.com/PolicyMic>`__).

Ruby
~~~~

-  `ruby-thumbor <https://rubygems.org/gems/ruby-thumbor>`__ - Ruby's
   gem to interact with thumbor server.
-  `thumbor\_rails <https://github.com/rafaelcaricio/thumbor_rails>`__ -
   Ruby's gem to make easier to generate urls in Rails projects.

Java
~~~~

-  `Pollexor <http://square.github.com/pollexor>`__ - Java client for
   the Thumbor image service which allows you to build URIs in an
   expressive fashion using a fluent API.
-

   .. raw:: html

      <del>

   `thumbor-enterprise-edition <https://github.com/heynemann/thumbor-enterprise-edition>`__
   - Java library to enable generating encrypted URLs. This library is
   deprecated in favor of
   `Pollexor <http://square.github.com/pollexor>`__.

   .. raw:: html

      </del>

PHP
~~~

-  `Thumbor-PHP <https://github.com/beeyev/thumbor-php>`__ - PHP implementation of URL generator for Thumbor. It also supports Laravel Framework.
-  `Phumbor <https://github.com/99designs/phumbor>`__ - A minimal PHP
   client for generating Thumbor URLs.
-  `Phumbor for Laravel <https://github.com/ceejayoz/laravel-phumbor>`__
   - A Laravel package providing a facade for Phumbor.
-  `Phumbor for Symfony2 <https://github.com/jbouzekri/PhumborBundle>`__
   - A Symfony2 Bundle providing a facade for Phumbor.

Swift
~~~~~

-  `Bumbo <https://github.com/guilhermearaujo/Bumbo>`__ - A swifty client
   for Thumbor

Objective-C
~~~~~~~~~~~

-  `OCThumbor <https://github.com/DanielHeckrath/OCThumbor>`__ -
   Objective-C for the Thumbor image service which allows you to build
   URIs in an expressive fashion using a fluent API.

.NET
~~~~
-  `DotNetThumbor <https://github.com/mi9/DotNetThumbor>`__ - DotNet client for the Thumbor image service.
   Provides an expressive fluent API.

Delphi
~~~~~~
-  `DelphiThumbor <https://github.com/marlonnardi/DelphiThumbor>`__ - Delphi class to thumbor. These are used to generate safe urls among others (by `Marlon Nardi <https://github.com/marlonnardi>`__).

Implementing a library
----------------------

If you want to provide a library to enable easy usage of thumbor in your
favorite programming language, please send an e-mail to
**thumbor@googlegroups.com** and we'll add it here.

Below are all the scenarios we think are worth testing automatically so
you can guarantee compatibility with thumbor. Please note that this is
not meant to be a replacement for TDD or for any other testing
methodology you might want to use. These are just helper scenarios that
we thought would help any library developers.

Library Tests - Generating HMAC of the URLs
-------------------------------------------

We sincerely advise you to have thumbor installed in your machine, so
you can implement a method in your tests that has thumbor generate a
signature for your URL so you can compare with your own signature. This
way you can make sure your url formatting and signing are working
properly.

Here's how it was implemented in Ruby:

::

    def sign_in_thumbor(key, str)
        #bash command to call thumbor's decrypt method
        command = "python3 -c 'from libthumbor.url_signers.base64_hmac_sha1 import UrlSigner; signer = UrlSigner(\"" << key << "\"); print(signer.signature(\"" << str << "\").decode(\"utf-8\"))'"

        #execute it in the shell using ruby's popen mechanism
        result = Array.new
        IO.popen(command) { |f| result.push(f.gets) }

        result.join('')
    end

You should be able to implement this easily in any modern programming
language. It makes for very reliable tests.

Library Tests - Scenarios
-------------------------

Remember that these are in pseudo-code (BDD-like) language, and not in
any programming language specifically.

Encryption Testing
~~~~~~~~~~~~~~~~~~

These scenarios assume that you separate the logic of composing the url
to be signed into a different "module", that is to be tested with the
URL Testing Scenarios after these scenarios.

Scenario 1 - Signing of a known url results
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

::

    Given
        A security key of 'my-security-key'
        And an image URL of "my.server.com/some/path/to/image.jpg"
        And a width of 300
        And a height of 200
    When
        I ask my library for a signed url
    Then
        I get '/8ammJH8D-7tXy6kU3lTvoXlhu4o=/300x200/my.server.com/some/path/to/image.jpg' as url

Scenario 2 - Thumbor matching of signature with my library signature
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

::

    Given
        A security key of 'my-security-key'
        And an image URL of "my.server.com/some/path/to/image.jpg"
        And a width of 300
        And a height of 200
    When
        I ask my library for an encrypted URL
    Then
        I get the proper url (/8ammJH8D-7tXy6kU3lTvoXlhu4o=/300x200/my.server.com/some/path/to/image.jpg)

Scenario 3 - Thumbor matching of signature with my library signature with meta
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

::

    Given
        A security key of 'my-security-key'
        And an image URL of "my.server.com/some/path/to/image.jpg"
        And the meta flag
    When
        I ask my library for an encrypted URL
    Then
        I get the proper url (/Ps3ORJDqxlSQ8y00T29GdNAh2CY=/meta/my.server.com/some/path/to/image.jpg)

Scenario 4 - Thumbor matching of signature with my library signature with smart
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

::

    Given
        A security key of 'my-security-key'
        And an image URL of "my.server.com/some/path/to/image.jpg"
        And the smart flag
    When
        I ask my library for an encrypted URL
    Then
        I get the proper url (/-2NHpejRK2CyPAm61FigfQgJBxw=/smart/my.server.com/some/path/to/image.jpg)

Scenario 5 - Thumbor matching of signature with my library signature with fit-in
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

::

    Given
        A security key of 'my-security-key'
        And an image URL of "my.server.com/some/path/to/image.jpg"
        And the fit-in flag
    When
        I ask my library for an encrypted URL
    Then
        I get the proper url (/uvLnA6TJlF-Cc-L8z9pEtfasO3s=/fit-in/my.server.com/some/path/to/image.jpg)

Scenario 6 - Thumbor matching of signature with my library signature with filters
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

::

    Given
        A security key of 'my-security-key'
        And an image URL of "my.server.com/some/path/to/image.jpg"
        And a 'quality(20)' filter
        And a 'brightness(10)' filter
    When
        I ask my library for an encrypted URL
    Then
        I get the proper url (/ZZtPCw-BLYN1g42Kh8xTcRs0Qls=/filters:brightness(10):contrast(20)/my.server.com/some/path/to/image.jpg)

You should test the same kind of tests for horizontal and vertical flip,
horizontal and vertical alignment and manual cropping.

More Information
----------------

-  :doc:`security`
