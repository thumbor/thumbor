Getting Started
===============

If you just want to give thumbor a try, it is pretty easy to get
started. **It won't take more than a minute.**

Just install it with ``pip install thumbor`` and start the process with
``thumbor`` in a console.

That's it! You are ready to start messing with images. Choose some image
online and try the following.

If you can't install thumbor locally, but can use virtualbox, take a
look at this repository:
https://github.com/torchbox/vagrant-thumbor-base.

This tutorial assumes the image you picked is
``http://www.waterfalls.hamilton.ca/images/Waterfall_Collage_home_sm1.jpg``.
Replace it with whatever image you want accordingly.

Changing its size
-----------------

Go to your browser and enter in the url:
``http://localhost:8888/unsafe/300x200/http://www.waterfalls.hamilton.ca/images/Waterfall_Collage_home_sm1.jpg``.

You should see the waterfall image with 300px of width and 200px of
height. Just play with it in the url to see the image change.

If you just want it to be proportional to the width, enter a height of
0, like:

``http://localhost:8888/unsafe/300x0/http://www.waterfalls.hamilton.ca/images/Waterfall_Collage_home_sm1.jpg``.

Flipping the image
------------------

How about seeing it backwards? Or upside down?

Go to your browser and enter in the url:
``http://localhost:8888/unsafe/-0x-0/http://www.waterfalls.hamilton.ca/images/Waterfall_Collage_home_sm1.jpg``.

You should see the waterfall backwards and upside down.

Filters
-------

What if I want to change contrast or brightness?

Go to your browser and enter in the url:
``http://localhost:8888/unsafe/filters:brightness(10):contrast(30)/http://www.waterfalls.hamilton.ca/images/Waterfall_Collage_home_sm1.jpg``.

There are many more filters to explore. Check the
:doc:`filters` page for more details.

What now?
---------

Ok, now that you know how amazing thumbor is, there's actually A LOT
more to it. Go check the rest of the docs to learn how to get even more
from your new imaging server.
