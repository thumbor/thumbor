Filters
=======

   .. ATTENTION::
    Filters are affecting each other in the order they are specified!
    If the original image has the size ``60x40`` and the thumbor url would look like:

    ``fit-in/100x100/filters:watermark(..):blur(..):fill(red,1):upscale()/http://some/image.jpeg``

    then the image will first checked if it fits into ``100x100`` (which it does), then
    gets the watermark, then it will be blurred (including the watermark), then
    filled with red so that it will use the ``100x100`` size and at the end upscaled will
    be applied without having any effect because fill was changing the size of the image
    already to the maximum available space.

.. toctree::
   :maxdepth: 1

   autojpg
   background_color
   blur
   brightness
   contrast
   convolution
   equalize
   extract_focal_points
   filling
   focal
   format
   grayscale
   max_bytes
   no_upscale
   noise
   proportion
   quality
   red_eye
   rgb
   rotate
   round_corners
   sharpen
   stretch
   strip_exif
   strip_icc
   upscale
   watermark
