## Installing

### Linux

1. `apt-get install gphoto2` on your Debian based distro
1. `yum install gphoto2` on your Fedora based distro

### macOS

1. [Install Homebrew](http://brew.sh/)
1. `brew install gphoto2`

## Running

Scanning script for the Noisebridge book scanner.
Captures and saves images from two cameras via the gphoto2 library.

To use, make a new directory for the book to be scanned, and run the
script from that directory. Images will be saved as imgXXXXX.jpg in
the current directory.

Images from both cameras are captured every time the enter key is
pressed. The script also writes out an html file which can be used
to view the images as they're scanned.
