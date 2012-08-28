rm -rf ./opencv
mkdir ./opencv
cd ./opencv
wget ftp://ftp.videolan.org/pub/videolan/x264/snapshots/last_stable_x264.tar.bz2
tar xjf last_stable_x264.tar.bz2
rm last_stable_x264.tar.bz2
cd `ls` # because directory name could be "last_stable_x264" or "x264-snapshot-20120824-2245-stable"
./configure --enable-static && make && sudo make install
if [ "$?" != "0" ]; then echo "Installation failed." && exit $?; fi
cd ..
rm -rf `ls`

wget http://ffmpeg.org/releases/ffmpeg-0.11.1.tar.gz
tar xzf ffmpeg-0.11.1.tar.gz
rm ffmpeg-0.11.1.tar.gz
cd ffmpeg-0.11.1
./configure --enable-gpl --enable-libfaac --enable-libmp3lame --enable-libopencore-amrnb --enable-libopencore-amrwb --enable-libtheora --enable-libvorbis --enable-libx264 --enable-libxvid --enable-nonfree --enable-postproc --enable-version3 --enable-x11grab && make && sudo make install
if [ "$?" != "0" ]; then echo "Installation failed." && exit $?; fi
cd ..
rm -rf ffmpeg-0.11.1

wget http://downloads.sourceforge.net/project/opencvlibrary/opencv-unix/2.4.1/OpenCV-2.4.1.tar.bz2
tar xjf OpenCV-2.4.1.tar.bz2
rm OpenCV-2.4.1.tar.bz2
cd OpenCV-2.4.1
mkdir release
cd release
cmake -D CMAKE_BUILD_TYPE=RELEASE -D CMAKE_INSTALL_PREFIX=/usr/local -D BUILD_PYTHON_SUPPORT=ON -D BUILD_EXAMPLES=ON .. && make && sudo make install
if [ "$?" != "0" ]; then echo "Installation failed." && exit $?; fi
cd ../../..
rm -rf opencv
