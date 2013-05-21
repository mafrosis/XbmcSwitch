#! /usr/bin/env python

import serial
import subprocess
import time

from subprocess import Popen, PIPE

PORT = "/dev/tty.usbmodemfd1121"
PORT = "/dev/ttyACM0"
PROC_NAME = "/usr/local/bin/xbmc"
INIT_SCRIPT_NAME = "xbmc"
RECONNECT_SLEEP = 5
MONITOR_SLEEP = 0.2


def enum(*sequential, **named):
    enums = dict(zip(sequential, range(len(sequential))), **named)
    return type('Enum', (), enums)

states = enum("CONNECTING", "RUNNING")


class SerialMonitor():
    ser = None
    state = None

    def __init__(self, port):
        self.port = port
        self.state = states.CONNECTING

    def connect(self):
        try:
            self.ser = serial.Serial(self.port, 9600, timeout=0)
            self.ser.setRTS(True)
            self.ser.setDTR(True)
        except serial.serialutil.SerialException:
            return False
        return True

    def monitor(self):
        try:
            xbmc_running = False

            # check xbmc running
            grep = Popen(['grep', PROC_NAME],
                stdin=Popen(['ps', '-ef'], stdout=PIPE).stdout,
                stdout=PIPE
            )
            out, err = grep.communicate()
            if len(out.strip()) > 0:
                procs = out.split("\n")
                for proc in procs:
                    if PROC_NAME in proc and 'grep' not in proc:
                        xbmc_running = True

            # read from serial port, when message received toggle XBMC running
            data = self.ser.readline()
            if len(data) > 0:
                if xbmc_running is False:
                    subprocess.call(['/etc/init.d/{0}'.format(INIT_SCRIPT_NAME), 'start'])
                else:
                    subprocess.call(['/etc/init.d/{0}'.format(INIT_SCRIPT_NAME), 'stop'])

            # write over serial to ignite LED
            if xbmc_running is True:
                self.ser.write('1')
            else:
                self.ser.write('0')

            # introduce a sensible delay
            time.sleep(0.2)

        except serial.SerialTimeoutException:
            pass
        except (OSError, serial.serialutil.SerialException):
            print "Disconnected"
            self.state = states.CONNECTING
            time.sleep(1)

    def run(self):
        self.alive = True

        try:
            while self.alive:
                if self.state == states.CONNECTING:
                    if self.connect():
                        print "Connected"
                        self.state = states.RUNNING
                    else:
                        time.sleep(RECONNECT_SLEEP)

                elif self.state == states.RUNNING:
                    self.monitor()
                    time.sleep(MONITOR_SLEEP)

        except KeyboardInterrupt:
            self.alive = False
        finally:
            if self.ser is not None:
                self.ser.close()


if __name__ == "__main__":
    sr = SerialMonitor(PORT)
    sr.run()
