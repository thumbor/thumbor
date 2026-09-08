# Welcome to Thumbor's documentation!

```{image} images/logo-thumbor.png
```

## What's Thumbor?

Thumbor is a smart imaging service. It enables on-demand crop, resizing and
flipping of images.

It features a VERY smart detection of important points in the image for better
cropping and resizing, using state-of-the-art face and feature detection
algorithms (more on that in {doc}`detection_algorithms`).

Using thumbor is very easy (after it is running). All you have to do is access
it using an URL for an image, like this:

```
http://thumbor-server/unsafe/300x200/smart/<url>
```

That URL would show an image of the Big Brother Brasil participants in 300x200
using smart crop. There are several other options to the image URL
configuration. You can check them in the {doc}`usage` page. For more details on
the /unsafe part of the URL, check the {doc}`security` page.

The safe url for the above URL would look like (check {doc}`security` for more
details):

```
http://thumbor-server/K97LekICOXT9MbO3X1u8BBkrjbu5/300x200/smart/<url>
```

```{warning}
Release 7.0.0 introduces a major breaking change due to the migration to
python 3 and the modernization of our codebase. Please read the
[release notes](https://github.com/thumbor/thumbor/releases/tag/7.0.0)
for details on how to upgrade.
```

## Contents

```{toctree}
---
maxdepth: 2
---
installing
getting_started
usage
imaging
customizing
administration
upload
more
```

## Indices and tables

- {ref}`genindex`
- {ref}`modindex`
- {ref}`search`
