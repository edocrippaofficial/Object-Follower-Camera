# Object Follower Camera

usage: pan_tilt_tracking.py (-f | -c low up | -p) [-na] [--dnn] [--camera src] [-h] 


optional arguments:
<pre>
  -h, --help            show this help message and exit
  -f, --face            track a human face
  -c low up, --color    track selected color (need lower and upper HSV values)
  -p, --pick            track a picked color
  -na                   run script without Arduino connected
  --dnn                 use a deep neural network instead of haar cascades for
                        tracking the face
  --camera src       select the camera source

</pre>

Python script that controls a pan-tilt camera trying to maintain the selected object in the center of the screen. Works with given RGB color or a human face using OpenCV's Haar Cascades or DNN.