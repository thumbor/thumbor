from ubuntu
maintainer joe@tanga.com
run echo "deb http://archive.ubuntu.com/ubuntu precise main universe" > /etc/apt/sources.list
run echo "deb http://ppa.launchpad.net/thumbor/ppa/ubuntu precise main" >> /etc/apt/sources.list
run apt-key adv --keyserver keyserver.ubuntu.com --recv-keys C6C3D73D1225313B
run apt-get update
run apt-get upgrade -y
run apt-get install thumbor -y

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
