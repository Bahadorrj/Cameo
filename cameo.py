import sys
import threading

import cv2
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication

from manager import CaptureManager, WindowManager


class Cameo(object):
    def __init__(self):
        self.windowManager = WindowManager('Cameo', self.onKeypress)
        self.captureManager = CaptureManager(cv2.VideoCapture(0), self.windowManager, True)

    def run(self):
        """Run the main loop."""
        while not self.windowManager.isClosed:
            self.captureManager.enterFrame()
            self.captureManager.exitFrame()

    def onKeypress(self, keycode):
        """Handle a keypress.
            space -> Take a screenshot.
            tab -> Start/stop recording a screencast.
            escape -> Quit.
            """
        if keycode == Qt.Key_Space:  # space
            self.captureManager.writeImage('screenshot.png')
            self.windowManager.changeStatus('Screenshot Saved!')
        elif keycode == Qt.Key_Tab:  # tab
            if not self.captureManager.isWritingVideo:
                self.captureManager.startWritingVideo('screencast.avi')
                self.windowManager.changeStatus('Started Recording!')
            else:
                self.captureManager.stopWritingVideo()
                self.windowManager.changeStatus('Stopped Recording!')
        elif keycode == Qt.Key_Escape:  # escape
            self.windowManager.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    cameo = Cameo()
    cameo.windowManager.show()
    threading.Thread(target=cameo.run).start()
    sys.exit(app.exec())
