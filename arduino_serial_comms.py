#! /usr/bin/env python

import logging
import serial
import time

from subprocess import Popen, PIPE

# Arduino serial port
SERIAL_PORT = "/dev/ttyACM{}"

# XBMC settings
PROC_NAME = "/usr/local/bin/xbmc"
INIT_SCRIPT_NAME = "xbmc"

# Logging
LOG_FILE = "/var/log/mafro/XbmcSwitch/{}.log"
LOG_LEVEL = logging.DEBUG

RECONNECT_SLEEP = 5
MONITOR_SLEEP = 0.5


def enum(*sequential, **named):
    enums = dict(zip(sequential, range(len(sequential))), **named)
    return type('Enum', (), enums)

states = enum("CONNECTING", "RUNNING")


class SerialMonitor():
    ser = None
    state = None
    logger = None
    last_connect_error = None

    def __init__(self, port, logger):
        self.port = port
        self.state = states.CONNECTING
        self.logger = logger

    def connect(self):
        for n in xrange(2):
            self.serial_number = n
            try:
                self.ser = serial.Serial(self.port.format(n), 9600, timeout=0)
                self.ser.setRTS(True)
                self.ser.setDTR(True)
                return True
            except serial.serialutil.SerialException as e:
                if LOG_LEVEL == logging.DEBUG:
                    logger.debug("Connect: {}".format(e))
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
                logger.info("Button press received on Serial port")

                # when message received toggle XBMC running
                if xbmc_running is True:
                    command = "stop"
                else:
                    command = "start"

                xbmc = Popen(['/etc/init.d/{0}'.format(INIT_SCRIPT_NAME), command],
                    stdin=PIPE,
                    stdout=PIPE
                )
                out, err = xbmc.communicate()
                logger.debug(out)
                if err is not None and err != '':
                    logger.debug(err)

            # write over serial to ignite LED
            if xbmc_running is True:
                self.ser.write('1')
            else:
                self.ser.write('0')

        except serial.SerialTimeoutException:
            pass
        except (OSError, serial.serialutil.SerialException) as e:
            logger.error("Disconnected ({}: {})".format(e.__class__.__name__, e))
            self.state = states.CONNECTING
            time.sleep(1)

    def run(self):
        self.alive = True

        try:
            while self.alive is True:
                if self.state == states.CONNECTING:
                    if self.connect():
                        logger.info("Connected to {}".format(SERIAL_PORT.format(self.serial_number)))
                        self.state = states.RUNNING
                    else:
                        logger.info("Connecting: {}".format(self.last_connect_error))
                        time.sleep(RECONNECT_SLEEP)

                elif self.state == states.RUNNING:
                    self.monitor()
                    time.sleep(MONITOR_SLEEP)

            logger.info("Terminated")

        except KeyboardInterrupt:
            self.alive = False
        finally:
            if self.ser is not None:
                self.ser.close()

    def terminate(self):
        self.alive = False


if __name__ == "__main__":
    # setup app logging
    logger = logging.getLogger("XbmcSwitch")
    logger.setLevel(LOG_LEVEL)
    handler = logging.FileHandler(LOG_FILE.format("app"))
    handler.setFormatter(
        logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    )
    logger.addHandler(handler)

    logger.info("Starting Arduino serial comms")

    # instantiate serial monitoring class
    sr = SerialMonitor(SERIAL_PORT, logger)
    sr.run()
