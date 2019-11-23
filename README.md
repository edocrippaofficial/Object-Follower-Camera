# Object Follower Camera

usage: pan_tilt_tracking.py [-h] (--duck | --face | --color low up) [--dnn]

optional arguments:
<pre>
  -h, --help      show this help message and exit
  --duck          track a duck
  --face          track a human face
  --color low up  track selected color (need lower and upper HSV values)
  --dnn           use a deep neural network instead of haar cascades for
                  tracking the face (useless for the duck)
</pre>

Python script that controls a pan-tilt camera trying to maintain the selected object in the center of the screen. Works with given RGB color or a human face using OpenCV's Haar Cascades or DNN.