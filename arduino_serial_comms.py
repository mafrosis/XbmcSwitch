#! /usr/bin/env python

import serial
import time

from subprocess import Popen, PIPE


PORT = "/dev/tty.usbmodemfd1121"
PROC_NAME = "/usr/local/bin/xbmc"
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
            data = self.ser.readline()
            if len(data) > 0:
                print data.strip()

            xbmc_running = False

            # check xbmc running
            grep = Popen(['grep', PROC_NAME],
                stdin=Popen(['ps', '-ef'], stdout=PIPE).stdout,
                stdout=PIPE
            )
            out, err = grep.communicate()
            if len(out.strip()) > 0:
                procs = out.split("\n")
                for p in procs:
                    if PROC_NAME in p:
                        xbmc_running = True

            # write over serial will ignite LED
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
                        print "Failed to connect"
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
