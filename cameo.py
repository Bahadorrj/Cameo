import sys
import threading

import cv2
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt

from manager import CaptureManager, WindowManager


class Cameo(object):
    def __init__(self):
        self.exit = False
        self.windowManager = WindowManager('Cameo', self.onKeypress)
        self.windowManager.windowClosed.connect(self.quit)
        self.captureManager = CaptureManager(cv2.VideoCapture(0), self.windowManager, True)
        self.windowManager.show()

    def run(self):
        """Run the main loop."""
        while not self.exit:
            self.captureManager.enterFrame()
            frame = self.captureManager.frame
            if frame is not None:
                # TODO: Filter the frame (Chapter 3).
                pass
            self.captureManager.exitFrame()

    def quit(self):
        self.exit = True

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
    threading.Thread(target=cameo.run).start()
    sys.exit(app.exec())
