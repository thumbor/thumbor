mkdir ./opencv
cd ./opencv
wget ftp://ftp.videolan.org/pub/videolan/x264/snapshots/last_stable_x264.tar.bz2
tar xjf last_stable_x264.tar.bz2
cd last_stable_x264
./configure --enable-static && make && sudo make install
cd ..
wget http://ffmpeg.org/releases/ffmpeg-0.11.1.tar.gz
tar xzf ffmpeg-0.11.1.tar.gz
cd ffmpeg-0.11.1
./configure --enable-gpl --enable-libfaac --enable-libmp3lame --enable-libopencore-amrnb --enable-libopencore-amrwb --enable-libtheora --enable-libvorbis --enable-libx264 --enable-libxvid --enable-nonfree --enable-postproc --enable-version3 --enable-x11grab && make && sudo make install
cd ..
wget http://downloads.sourceforge.net/project/opencvlibrary/opencv-unix/2.4.1/OpenCV-2.4.1.tar.bz2
tar xjf OpenCV-2.4.1.tar.bz2
cd OpenCV-2.4.1
mkdir release
cd release
cmake -D CMAKE_BUILD_TYPE=RELEASE -D CMAKE_INSTALL_PREFIX=/usr/local -D BUILD_PYTHON_SUPPORT=ON -D BUILD_EXAMPLES=ON .. && make && sudo make install
cd ../../..
