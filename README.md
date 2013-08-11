XbmcSwitch
==========

Run an external switch to start/stop a program on linux - in this case XBMC on a headless linux box.


Installation
------------

The `XbmcSwitch.ino` file needs to be flashed on to your Arduino, and then on the server side you'll want to symlink the `config/XbmcSwitch.init` script to `/etc/init.d/XbmcSwitch`. Then you can start the app with `/etc/init.d/XbmcSwitch start`.

I recommend creating a virtualenv for the app, and installing pySerial as specified in `config/requirements.txt`. Otherwise you could install pySerial globally on your system and modify `DAEMON` as specified below.

A couple of variables will need changing in the init script for your setup:

 * `DAEMON` is the path to the Python binary running this app. It may be /usr/bin/python or a virtualenv specific one like mine.
 * `DAEMON_OPTS` is the path to the `arduino_serial_comms.py` script.

The `arduino_serial_comms.py` script does all the hard work on the server, and has a few globals you will want to edit:

 * `SERIAL_PORT` is the path to serial comms port. Note the {0} place holder which will be filled with either 0 or 1 at runtime.
 * `PROC_NAME` is the name of the running process which the switch controls. This value is grepped for in `ps`.
 * `INIT_SCRIPT_NAME` is the init script which starts `PROC_NAME`.
 * `LOG_FILE` is the location of the scripts logging. You'll want to change this.
 * `LOG_LEVEL` may be set to `logging.INFO` after successful setup.


Extra System Configuration
--------------------------

I modified my XBMC start script to create its pid file in a directory owned by my user (which runs the `arduino_serial_comms.py` script).

    # Path of the PID file
    PID_FILE=/var/run/xbmc/xbmc.pid
    if [ ! -d /var/run/xbmc ]; then
        mkdir /var/run/xbmc    
        /bin/chown mafro:mafro /var/run/xbmc    
        /bin/chmod 755 /var/run/xbmc    
    fi


License
-------

Copyright (C) 2013 Matt Black

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
