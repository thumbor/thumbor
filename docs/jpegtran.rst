jpegtran
==========

Jpegtran is a lossless jpeg optimizer which can make your jpegs smaller by optimizing DCT coefficients. Information on jpegtran can be a bit difficult to find but the linux man page is pretty good: https://linux.die.net/man/1/jpegtran

Jpegtran can be used in conjunction with Thumbor. If the optimizer has been activated, Thumbor will first process your jpeg normally then it will hand the jpeg off to jpegtran for further optimizations before Thumbor returns the final image.

To use jpegtran with Thumbor you must first install jpegtran, various linux distros often provide a package by the same name or it can be installed from source. You should make sure that jpegtran is in PATH, do a `which jpegtran` and you should see an absolute path where the jpegtran resides. It is also possible to use mozjpeg's version of jpegtran as a drop-in replacement of libjpeg-turbo's version.

You also need to enable the Thumbor jpegtran optimizer in your thumbor.conf, like so:

.. code-block:: python

  OPTIMIZERS = [
    'thumbor.optimizers.jpegtran'
  ]


You can also manually specify the jpegtran path, like this:

.. code-block:: python

  JPEGTRAN_PATH=/usr/local/bin/jpegtran

Once activated, no extra url parameters are needed - jpegtran will run on all jpegs automatically. If you have opted to use progressive jpegs via the ``PROGRESSIVE_JPEG`` option, jpegtran will also honor and product progressive jpegs.

It is possible to supply progressive scans file via ``JPEGTRAN_SCANS_FILE`` config option.
