#! /usr/bin/env python

import serial
import time

from subprocess import Popen, PIPE

# Arduino serial port
SERIAL_PORT = "/dev/ttyACM{0}"
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
    last_connect_error = None

    def __init__(self, port):
        self.port = port
        self.state = states.CONNECTING

    def connect(self):
        for n in xrange(2):
            try:
                self.ser = serial.Serial(self.port.format(n), 9600, timeout=0)
                self.ser.setRTS(True)
                self.ser.setDTR(True)
                return True
            except serial.serialutil.SerialException as e:
                self.last_connect_error = str(e)
        return False

    def monitor(self):
        try:
            xbmc_running = False

            # check xbmc running
            grep = Popen(['/bin/grep', PROC_NAME],
                stdin=Popen(['/bin/ps', '-ef'], stdout=PIPE).stdout,
                stdout=PIPE
            )
            out, err = grep.communicate()
            if len(out.strip()) > 0:
                procs = out.split("\n")
                for proc in procs:
                    if PROC_NAME in proc and 'grep' not in proc:
                        xbmc_running = True

            # read from serial port
            data = self.ser.readline()
            if len(data) > 0:
                print "Button press received on Serial port"

                # when message received toggle XBMC running
                xbmc = Popen(['/etc/init.d/{0}'.format(INIT_SCRIPT_NAME), 'start'],
                    stdin=PIPE,
                    stdout=PIPE
                )
                out, err = xbmc.communicate()

            # write over serial to ignite LED
            if xbmc_running is True:
                self.ser.write('1')
            else:
                self.ser.write('0')

            # introduce a sensible delay
            time.sleep(0.2)

        except serial.SerialTimeoutException:
            pass
        except (OSError, serial.serialutil.SerialException) as e:
            print "Disconnected ({0}: {1})".format(e.__class__.__name__, e)
            self.state = states.CONNECTING
            time.sleep(1)

    def run(self):
        self.alive = True

        try:
            while self.alive is True:
                if self.state == states.CONNECTING:
                    if self.connect():
                        print "Connected"
                        self.state = states.RUNNING
                    else:
                        print "Connecting: {0}".format(self.last_connect_error)
                        time.sleep(RECONNECT_SLEEP)

                elif self.state == states.RUNNING:
                    self.monitor()
                    time.sleep(MONITOR_SLEEP)

        except KeyboardInterrupt:
            self.alive = False
        finally:
            if self.ser is not None:
                self.ser.close()

    def terminate(self):
        self.alive = False


if __name__ == "__main__":
    print "Starting Arduino serial comms on port {0}".format(PORT)
    sr = SerialMonitor(PORT)
    sr.run()
