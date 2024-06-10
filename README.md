## Hello there
This is an application, which goal is to detect and track objects in a video source.

### How to run the app
The application is a python script, therefor it is necessary to have already installed the correct packages. Once done, you can run the application.

#### Preparation
Please create your own [[venv]](https://docs.python.org/3/library/venv.html) and activate it.
Right after, install all the needed packages via:
```bash
pip install -r requirements.txt
```

Since then you have everything needed to run the application.

#### Run the app

By default, you can run the application via:
```bash
python app.py
```
By recommendation, run the application as follows:
```bash
python app.py --path-name {{YOUR-PATH}}/task_video.mp4 --show-coordinates True --show-contours True --show-info True --show-path True --show-realtime True
```

However, it is required to determine flags so the application can proceed correctly.

Flags:
* --path-name: 
    * description: A path to your video source on which objects will be detected
    * REQUIRED
* --show-coordinates:
    * description: The app will write into each frame's coordinates of detected objects.
    * default: **False**
* --show-contours:
    * description: The app will write into each frame's contours outline of detected objects.
    * default: **False**
* --show-info:
    * description: The app will write into each frame's information about tracked and detected objects.
    * default: **False**
* --show-path:
    * description: The app will write into each frame's followed path of each object.
    * default: **False**
* --show-whole-path:
    * description: The app will write into each frame's followed path of each object across the whole time when they have been detected.
    * default: **False**
* --show-realtime:
    * description: The app will prompt frames to a visible window.
    * default: **False**
* --save-as-video:
    * description: The app will save the output video into a source video path under this name.
    * value: *name of output video file*
    * default: **output.mp4**
* --save-as-codec:
    * description: The app will save the output video created by this codec.
    * value: *name of output video codec*
    * default_value: **mp4v** 
    * caution: The ability to create a video is limited to already installed codecs. Please follow [[this link]](https://fourcc.org/codecs.php#letter_m) to choose the best codec for your platform.


### How to use the Object Detection
If you have already run the application, everything that you need to detect objects is specified correct flags as follows:

Full command in line:
`python app.py --show-coordinates True --show-contours True`

### How to use the Object Tracking
If you have already run the application, everything that you need to track objects is specified correct flags as follows:

Full command in line:
`python app.py --show-info True --show-path True`
or
`python app.py --show-info True --show-whole-path True`

### How to use Output Visualization
If you have already run the application, everything that you need to track objects is specified correct flags as follows:

Full command in line:
`python app.py --show-realtime True --save-as-video output --save-as-codec mpv4`
