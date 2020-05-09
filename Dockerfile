
FROM ubuntu:18.04

LABEL key="latest"
LABEL Maintainer="Allan Bikundo <allanbikundo@scalum.co.ke>"
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update -y && apt-get upgrade -y
RUN apt-get install -y python-pip
# ssl packages
RUN apt-get install -y libcurl4-openssl-dev libssl-dev
# computer vision packages
RUN apt-get install -y python-opencv libopencv-dev
# image format packages
RUN apt-get install -y libjpeg-dev libpng-dev libwebp-dev webp
# Install Thumbor
RUN pip install thumbor
#Get Curl
RUN apt-get install curl
# Thumbor Config with auto web p on
RUN curl -o thumbor.conf https://gist.githubusercontent.com/Allanbikundo/fc8b5698615b3fb8282bf901d4557326/raw/thumbor.conf

# ENTRYPOINT ["thumbor --conf /thumbor.conf"]

EXPOSE 8888
