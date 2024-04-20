import time

import cv2

from PyQt5.QtCore import QSize, pyqtSignal, Qt
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QMainWindow, QLabel, QFrame, QStatusBar


class CaptureManager(object):
    def __init__(self, capture, previewWindowManager=None, shouldMirrorPreview=False):
        self.previewWindowManager = previewWindowManager
        self.shouldMirrorPreview = shouldMirrorPreview
        self._capture = capture
        self._channel = 0
        self._enteredFrame = False
        self._frame = None
        self._imageFilename = None
        self._videoFilename = None
        self._videoEncoding = None
        self._videoWriter = None
        self._startTime = None
        self._framesElapsed = 0
        self._fpsEstimate = None

    @property
    def channel(self):
        return self._channel

    @channel.setter
    def channel(self, value):
        if self._channel != value:
            self._channel = value
            self._frame = None

    @property
    def frame(self):
        if self._enteredFrame and self._frame is None:
            # Decodes and returns the grabbed video frame
            _, self._frame = self._capture.retrieve(self._frame, self.channel)
        return self._frame

    @property
    def isWritingImage(self):
        return self._imageFilename is not None

    @property
    def isWritingVideo(self):
        return self._videoFilename is not None

    def enterFrame(self):
        """Capture the next frame, if any."""
        # But first, check that any previous frame was exited.
        assert not self._enteredFrame, 'previous enterFrame() had no matching exitFrame()'
        if self._capture is not None:
            # Grabs the next frame from video file or capturing device, return bool depending on the succession
            self._enteredFrame = self._capture.grab()

    def exitFrame(self):
        """Draw to the window. Write to files. Release the frame."""
        # Check whether any grabbed frame is retrievable.
        # The getter may retrieve and cache the frame.
        if self.frame is None:
            self._enteredFrame = False
            return
        # Update the FPS estimate and related variables.
        if self._framesElapsed == 0:
            self._startTime = time.time()
        else:
            timeElapsed = time.time() - self._startTime
            self._fpsEstimate = self._framesElapsed / timeElapsed
        self._framesElapsed += 1
        # Draw to the window, if any.
        if self.previewWindowManager is not None:
            self.previewWindowManager.displayContent(self.frame, self.shouldMirrorPreview)
        # Write to the image file, if any.
        if self.isWritingImage:
            cv2.imwrite(self._imageFilename, self._frame)
            self._imageFilename = None
        # Write to the video file, if any.
        self._writeVideoFrame()
        # Release the frame.
        self._frame = None
        self._enteredFrame = False

    def writeImage(self, filename):
        """Write the next exited frame to an image file."""
        self._imageFilename = filename

    def startWritingVideo(self, filename, encoding=cv2.VideoWriter.fourcc('M', 'J', 'P', 'G')):
        """Start writing exited frames to a video file."""
        self._videoFilename = filename
        self._videoEncoding = encoding

    def stopWritingVideo(self):
        """Stop writing exited frames to a video file."""
        self._videoFilename = None
        self._videoEncoding = None
        self._videoWriter = None

    def _writeVideoFrame(self):
        if not self.isWritingVideo:
            return
        if self._videoWriter is None:
            fps = self._capture.get(cv2.CAP_PROP_FPS)
            if fps <= 0.0:
                # The capture's FPS is unknown so use an estimate.
                if self._framesElapsed < 20:
                    # Wait until more frames elapse so that the estimate is more stable.
                    return
                else:
                    fps = self._fpsEstimate
            size = (int(self._capture.get(cv2.CAP_PROP_FRAME_WIDTH)),
                    int(self._capture.get(cv2.CAP_PROP_FRAME_HEIGHT)))
            self._videoWriter = cv2.VideoWriter(self._videoFilename, self._videoEncoding, fps, size)
        self._videoWriter.write(self._frame)


class WindowManager(QMainWindow):
    windowClosed = pyqtSignal()

    def __init__(self, windowName, keypressCallback=None):
        super().__init__()
        self.keypressCallback = keypressCallback
        self.setWindowTitle(windowName)
        self.setMinimumSize(QSize(640, 480))
        self._media = QLabel(self)
        self._media.setFrameShape(QFrame.Shape.Box)
        self.setCentralWidget(self._media)
        self._statusbar = QStatusBar(self)
        self.setStatusBar(self._statusbar)

    def displayContent(self, content, shouldMirrorPreview):
        # Convert numpy array to QImage
        height, width, channels = content.shape
        bytes_per_line = channels * width
        image = QImage(content.data, width, height, bytes_per_line, QImage.Format_BGR888)

        if shouldMirrorPreview:
            image = image.mirrored(horizontal=True, vertical=False)

        # Convert QImage to QPixmap
        pixmap = QPixmap.fromImage(image).scaled(self.size(), aspectRatioMode=Qt.KeepAspectRatio)

        # Set the pixmap on the QLabel test
        self._media.setPixmap(pixmap)

    def changeStatus(self, status: str):
        self._statusbar.showMessage(status)

    def keyPressEvent(self, a0):
        keycode = a0.key()
        self.keypressCallback(keycode)

    def closeEvent(self, a0):
        self.windowClosed.emit()
