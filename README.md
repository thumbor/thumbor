<h4 align="center">Join <a href="https://github.com/thumbor/thumbor-bootcamp">thumbor-bootcamp</a> for a learning and contribution experience with ❤️ and 🤗 from the thumbor team</h4>

<p align="center">
  <a href="http://www.thumbor.org">
    <img title="thumbor" alt="thumbor" src="./docs/thumbor-logo.png" />
  </a>
</p>

<h3 align="center">
Crop, resize, transform and much more, all on-demand and AI Powered
</h3>

<p align="center">
  <img src='https://github.com/thumbor/thumbor/workflows/build/badge.svg' />
  <a href='https://coveralls.io/github/thumbor/thumbor?branch=master' target='_blank'>
    <img src='https://coveralls.io/repos/thumbor/thumbor/badge.svg?branch=master&service=github'/>
  </a>
  <a href='https://codeclimate.com/github/thumbor/thumbor' target='_blank'>
    <img src='https://codeclimate.com/github/thumbor/thumbor/badges/gpa.svg'/>
  </a>
  <a href='https://pypi.python.org/pypi/thumbor' target='_blank'>
    <img src='https://img.shields.io/pypi/v/thumbor.svg'/>
  </a>
  <br />
  <a href='https://github.com/thumbor/thumbor/pulls' target='_blank'>
    <img src='https://img.shields.io/github/issues-pr-raw/thumbor/thumbor.svg'/>
  </a>
  <a href='https://github.com/thumbor/thumbor/issues' target='_blank'>
    <img src='https://img.shields.io/github/issues-raw/thumbor/thumbor.svg'/>
  </a>
  <a href='https://pypi.python.org/pypi/thumbor' target='_blank'>
    <img src='https://img.shields.io/pypi/dm/thumbor.svg'/>
  </a>
</p>

<h4 align="center">thumbor is trusted by hundreds of companies worldwide</h4>
<p align="center">
  <img src="./docs/wikipedia.png" alt="Wikipedia trusts thumbor" title="Wikipedia trusts thumbor" width="128" height="128" />&nbsp;
  <img src="./docs/globocom.png" alt="Globo.com trusts thumbor" title="Globo.com trusts thumbor" width="128" height="128" />&nbsp;
  <img src="./docs/vox.png" alt="Vox Media trusts thumbor" title="Vox Media trusts thumbor" width="128" height="128" />&nbsp;
  <img src="./docs/forbes-logo.png" alt="Forbes trusts thumbor" title="Forbes trusts thumbor" width="128" height="128" />&nbsp;
  <img src="./docs/squareup.png" alt="Square trusts thumbor" title="Square trusts thumbor" width="128" height="128" />&nbsp;
  <img src="./docs/deliveroo.png" alt="Deliveroo trusts thumbor" title="Deliveroo trusts thumbor" width="128" height="128" />&nbsp;
  <img src="./docs/canalplus.png" alt="Canal+ trusts thumbor" title="Canal+ trusts thumbor" width="128" height="128" />&nbsp;
  <img src="./docs/terra.png" alt="Terra trusts thumbor" title="Terra trusts thumbor" width="128" height="128" />&nbsp;
  <img src="./docs/nrc.png" alt="nrc trusts thumbor" title="nrc trusts thumbor" width="128" height="128" />&nbsp;
  <img src="./docs/webdev.png" alt="web.dev indicates thumbor for high-performance web sites" title="web.dev indicates thumbor for high-performance web sites" width="128" height="128" />&nbsp;
  <img src="./docs/aws.png" alt="aws indicates thumbor for serverless image handling" title="aws indicates thumbor for serverless image handling" width="128" height="128" />
  <br />
  and many more!
</p>

thumbor is a smart imaging service that enables on-demand [cropping, resizing, applying filters and optimizing](http://thumbor.readthedocs.io/en/latest/crop_and_resize_algorithms.html) images.

Cropping photos automatically can be a frustrating experience with severed heads involved. thumbor
uses [AI for smart detection](http://thumbor.readthedocs.io/en/latest/detection_algorithms.html).

thumbor is an HTTP server and you can create as many different images as you want just by varying path parameters:

```
http://<thumbor-server>/300x200/smart/thumbor.readthedocs.io/en/latest/_images/logo-thumbor.png
```

You should see an image of the thumbor logo in 300x200.

Learn more about all you can do in [thumbor's documentation](http://thumbor.readthedocs.io/en/latest/index.html "thumbor docs").

## ⚙️ Installation

Decide which installation option you want to use.

### Option 1: pip

```bash
# thumbor with main dependencies only
pip install thumbor

# thumbor with OpenCV dependency
pip install thumbor[opencv]

# thumbor with all dependencies
pip install thumbor[all]
```

### Option 2: Binary

Available as a package in the official repositories of
distributions such as
[Debian](https://packages.debian.org/source/sid/thumbor) and
[Ubuntu](https://launchpad.net/ubuntu/+source/thumbor).

```bash
sudo apt update
sudo apt install thumbor
```

### Option 3: Docker

An official Docker image is available on GitHub Container Registry:

```bash
docker run -p 8888:8888 ghcr.io/thumbor/thumbor:latest
```

For more information about the Docker image and available tags, visit the [GitHub Container Registry](https://github.com/thumbor/thumbor/pkgs/container/thumbor).

For more ways, please check out [Installation](https://thumbor.readthedocs.io/en/latest/installing.html).

### Run

Running it is as easy as hit:

```bash
thumbor
```

After this, you can reach it on http://localhost:8888/unsafe/https://raw.githubusercontent.com/thumbor/thumbor/master/example.jpg

### Troubles?

If you experience any troubles, try running:

```bash
thumbor-doctor
```

If you have a `thumbor.conf` file, you can use that to help thumbor-doctor:

```bash
thumbor-doctor -c thumbor.conf
```

If you still need help, please [raise an issue](https://github.com/thumbor/thumbor/issues). Remember to send your `thumbor-doctor` output in the issue:

```bash
thumbor-doctor --nocolor -c thumbor.conf
```

## 🎯 Features

- supports all common images formats out of the box
- [intelligent cropping and resizing](http://thumbor.readthedocs.io/en/latest/detection_algorithms.html)
- blazing fast using caching
- supports many storages (local storage, AWS S3, Rackspace, Ceph, ...)
- AI-powered cropping based on face and feature detection (glasses, interesting points, ...)
- integrated with many programming languages and frameworks <img src="https://www.python.org/favicon.ico" width="16" height="16" /><img src="https://nodejs.org/static/images/favicons/favicon.png" width="16" height="16" /><img src="https://rubygems.org/favicon.ico" width="16" height="16" /> and many more...
- [highly extensible](https://thumbor.readthedocs.io/en/latest/customizing.html)

## 🌟 Awesome Goodies

[awesome-thumbor](https://github.com/thumbor/awesome-thumbor) is a curated list of all things thumbor. There you can find filters, storages, engines, loaders, docker images, extensions in your favorite language and framework, and much more.

All of it with a clear indication of each project's quality. Have fun!

## 👍 Contribute

thumbor is an open-source project with many contributors. Join them
[contributing code](https://github.com/thumbor/thumbor/blob/master/CONTRIBUTING.md) or
[contributing documentation](https://github.com/thumbor/thumbor/blob/master/CONTRIBUTING.md).

If you use thumbor, please take 1 minute and answer [this survey](http://t.co/qPBLXJX0mi)? Only 2 questions!

Join the chat at https://gitter.im/thumbor/thumbor

## 👀 Demo

You can see thumbor in action at http://thumborize.me/
