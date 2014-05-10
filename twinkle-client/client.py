import sys
import getopt
import platform
import subprocess

from twisted.internet import reactor
from autobahn.twisted.websocket import WebSocketClientFactory, WebSocketClientProtocol, connectWS

STAR_REQUEST_TIMEOUT_IN_SECONDS = 3
DEFAULT_URL = "ws://localhost:9000"

STAR_REQUEST_MESSAGE = "twinkle:star"
ERROR_MESSAGE = "twinkle:error"
STARRED_MESSAGE = "twinkle:starred"

def _enum(**enums):
    return type('Enum', (), enums)
Sound = _enum(SUCCESS = 1, FAIL = 2)

muted = False

class ClientProtocol(WebSocketClientProtocol):

    def __init__(self):
        self.has_recived_starred_message = False

    def onOpen(self):
        self.sendMessage(STAR_REQUEST_MESSAGE)
        reactor.callLater(STAR_REQUEST_TIMEOUT_IN_SECONDS, self.timeout)

    def onClose(self, wasClean, code, reason):
        if not wasClean:
            terminateAbnormally(reason)
        elif self.has_recived_starred_message == False:
            terminateAbnormally("Star request failed")
        else:
            reactor.stop()

    def onMessage(self, message, binary):
        if message == ERROR_MESSAGE:
            self.sendClose()
        elif message == STARRED_MESSAGE:
            self.has_recived_starred_message = True
            print("Star request succeeded")
            if not muted:
                playSound(Sound.SUCCESS)
            self.sendClose()

    def timeout(self):
        if not self.has_recived_starred_message:
            print("Timeout while waiting for star request's response")
            self.sendClose()


class ClientFactory(WebSocketClientFactory):
    def __init__(self, url):
        WebSocketClientFactory.__init__(self, url)

    def clientConnectionFailed(self, connector, reason):
        terminateAbnormally(reason)


def terminateAbnormally(reason):
    print(reason)
    if not muted:
        playSound(Sound.FAIL)
    reactor.stop()

def playSound(sound):
    if (sound == Sound.SUCCESS):
        audioFile = "success.wav"
    elif (sound == Sound.FAIL):
        audioFile = "fail.wav"
    else:
        raise Exception("Unknown sound state")
    try:
        playCommand = getPlayCommand(audioFile)
        subprocess.call(playCommand, shell=True)
    except Exception as e:
        print(e)

def getPlayCommand(filePath):
    system = platform.system()
    if system == "Linux":
        return "aplay " + filePath
    # TODO Needs testing
    elif system == "Darwin":
        return "afplay " + filePath
    elif system == "Windows":
        return "powershell -c (New-Object Media.SoundPlayer \"" + filePath + "\").PlaySync();"
    else:
        raise Exception("Could not identify platform while trying to play audio")


if __name__ == '__main__':
    url = DEFAULT_URL

    argv = sys.argv[1:]
    try:
        opts, args = getopt.getopt(argv,"mh", ["url=", "mute-sound", "help"])
    except getopt.GetoptError:
        print('twinkle [--url=<url to web socket server>] [-m|--mute-sound] [-h|--help]')
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print('twinkle [--url=<url to web socket server>] [-m|--mute-sound] [-h|--help]')
            sys.exit()
        elif opt in ("--url"):
            url = arg
        elif opt in ("-m", "--mute-sound"):
            muted = True

    factory = ClientFactory(url)
    factory.protocol = ClientProtocol
    connectWS(factory)
    reactor.run()
