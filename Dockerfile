from ubuntu:12.04
maintainer joe@tanga.com
run echo "deb http://archive.ubuntu.com/ubuntu precise main universe" > /etc/apt/sources.list
run echo "deb http://ppa.launchpad.net/thumbor/ppa/ubuntu precise main" >> /etc/apt/sources.list
run apt-key adv --keyserver keyserver.ubuntu.com --recv-keys C6C3D73D1225313B
run apt-get update
run apt-get upgrade -y
run apt-get install graphicsmagick -y
run apt-get install thumbor -y

######### BEGIN OpenCV Install. Is this the best way?
run apt-get install libtbb2 libtbb-dev  -y
run apt-get install libgtk2.0-dev build-essential pkg-config  -y
run apt-get install libpng12-0 libpng12-dev libpng++-dev libpng3 libpnglite-dev  -y
run apt-get install zlib1g-dbg zlib1g zlib1g-dev  -y
run apt-get install libjasper-dev libjasper-runtime libjasper1  -y
run apt-get install pngtools libtiff4-dev libtiff4 libtiffxx0c2 libtiff-tools  -y
run apt-get install libjpeg62 libjpeg62-dev libjpeg62-dbg libjpeg-progs  -y
run apt-get install ffmpeg libavcodec-dev libavformat-dev  -y
run apt-get install libgstreamer0.10-0-dbg libgstreamer0.10-0 libgstreamer0.10-dev  -y
run apt-get install libgstreamer-plugins-base0.10-dev libxine1-ffmpeg libxine-dev  -y
run apt-get install libxine1-bin libunicap2 libunicap2-dev libdc1394-22-dev libdc1394-22  -y
run apt-get install libdc1394-utils swig libv4l-0 libv4l-dev python-numpy libpython2.7  -y
run apt-get install python-dev python2.7-dev openexr libswscale-dev  -y
run apt-get install libeigen2-dev libopenexr-dev cmake -y
run apt-get install wget -y
run curl -L http://sourceforge.net/projects/opencvlibrary/files/opencv-unix/2.2/OpenCV-2.2.0.tar.bz2 | tar xj
run mkdir OpenCV-2.2.0/release 
run cd OpenCV-2.2.0/release && cmake -D CMAKE_BUILD_TYPE=RELEASE -D WITH_TBB=ON -D TBB_INCLUDE_DIRS=/usr/include/tbb CMAKE_INSTALL_PREFIX=/usr/local -D BUILD_PYTHON_SUPPORT=ON -D WITH_GTK=ON -D BUILD_EXAMPLES=ON ..
run cd OpenCV-2.2.0/release && make -j 2 && make install && ldconfig
run mv /usr/local/lib/python2.7/site-packages/cv.so /usr/local/lib/python2.7/dist-packages/cv.so
######### END OpenCV Install

# Used to install the python fix below.
run apt-get install curl -y 

# so we can login to docker container and poke around at files easily..
run apt-get install vim -y 

# Some python error when running thumbor, not sure why.
# "ImportError: No module named pkg_resources"
# Ugly fix from http://stackoverflow.com/questions/7446187/no-module-named-pkg-resources
run curl https://bitbucket.org/pypa/setuptools/raw/bootstrap/ez_setup.py | python

# Allow unsafe URLs for now
run sed -i 's/ALLOW_UNSAFE_URL = False/ALLOW_UNSAFE_URL = True/g' /etc/thumbor.conf


expose 8888
cmd thumbor

# Run with 
# sudo docker run -p 80:8888 <image_id>
