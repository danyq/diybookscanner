#!/usr/bin/env python
#
# Scanning script for the Noisebridge book scanner.

import sys
import subprocess
import re
import time
import os

GPHOTO = 'gphoto2'
VIEW_FILE = 'view.html'
TMP_FILE = 'view_tmp.html'
IMG_FORMAT = 'img%05d.jpg'
TMP_FORMAT = 'tmp%05d.jpg'

def snap(camera, filename):
    '''Starts a process to capture and save an image with the given
    camera.'''
    return subprocess.Popen([GPHOTO, '--capture-image-and-download',
                             '--force-overwrite', '--port', camera,
                             '--filename', filename])

def wait(process1, process2):
    '''Wait for the two processes to end.'''
    while process1.poll() is None or process2.poll() is None:
        time.sleep(0.1)
    assert process1.returncode == 0 and process2.returncode == 0

def write_html(images, background_color='fff'):
    '''Writes out an html file showing the given list of images.'''
    f = open(TMP_FILE, 'w')
    f.write('''<!doctype html>
<html><head><META HTTP-EQUIV="refresh" CONTENT="1"><style>
body {{ text-align:center; background-color:#{color}; }}
div {{ float:left; width:48%; }}
</style></head><body>'''.format(color=background_color))
    for image in images:
        f.write('<div>{img}<br><img src="{img}" width="100%"></div>'.format(img=image))
    f.write('</body></html>')
    f.close()
    os.rename(TMP_FILE, VIEW_FILE)

def show(img_num, background_color='fff'):
    '''Update the html file to show the given left-side image, the
    corresponding right-side image, and the previous pair of images ifIMG_FORMAT
    applicable. The provided image number must be even (for the left
    side).'''
    assert img_num % 2 == 0
    if img_num < 2:
	write_html([IMG_FORMAT % 0, IMG_FORMAT % 1], background_color)
    else:
        write_html([IMG_FORMAT % img_num, IMG_FORMAT % (img_num + 1),
                    IMG_FORMAT % (img_num - 2), IMG_FORMAT % (img_num - 1)],
                   background_color)

# On Mac, the PTPCamera process takes control of the camera, so kill it.
devnull = open(os.devnull, 'w')
subprocess.call(["killall", "PTPCamera"], stderr=devnull)  # ignore output
devnull.close()

print 'detecting cameras'
gphoto_output = subprocess.check_output([GPHOTO, '--auto-detect'])
cameras = re.findall('usb:\d*,\d*', gphoto_output)
if len(cameras) is not 2:
    print 'Failed to find two cameras. Results for "'+GPHOTO+' --auto-detect":'
    print gphoto_output
    sys.exit(1)
left_cam, right_cam = cameras

print 'capturing preview images'
p1 = snap(left_cam, TMP_FORMAT % 0)
p2 = snap(right_cam, TMP_FORMAT % 1)
wait(p1, p2)
write_html([TMP_FORMAT % 0, TMP_FORMAT % 1])
print
print 'view images here:'
print 'file://' + os.path.realpath(VIEW_FILE)
print
if raw_input('switch cameras? (y/N) ')[:1].lower() == 'y':
    left_cam, right_cam = right_cam, left_cam

# main scanning loop
img_num = 0
while True:
    x = raw_input('\nReady. Press enter to capture, image number to jump, q to quit: ')
    if x == 'q':  # clean up and quit
        os.remove(TMP_FORMAT % 0)
        os.remove(TMP_FORMAT % 1)
        os.remove(VIEW_FILE)
        break
    if x == '':  # take next picture
        p1 = snap(left_cam, IMG_FORMAT % img_num)
        p2 = snap(right_cam, IMG_FORMAT % (img_num + 1))
        show(img_num, 'f99')  # red background: cameras not ready
        wait(p1, p2)
        show(img_num, '9f9')  # green background: cameras ready
	rightpic = "img" + str(img_num).zfill(5) + ".jpg"
	leftpic = "img" + str(img_num+1).zfill(5) + ".jpg"
	os.system("jpegtran -rot 270 "+rightpic+" > opt-" + rightpic)
	os.system("cp opt-"+rightpic+" "+rightpic)
	os.system("rm opt-"+rightpic)
	os.system("jpegtran -rot 90 "+leftpic+" > opt-" + leftpic)
	os.system("cp opt-"+leftpic+" "+leftpic)
	os.system("rm opt-"+leftpic)
	img_num += 2
        continue
    try:  # assume x is an image number to jump to
        img_num = int(x) // 2 * 2  # convert to even number
    except ValueError:
        print 'unrecognized command'
        continue
