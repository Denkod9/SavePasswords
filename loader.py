from PyQt5.QtCore import Qt
from PyQt5.QtGui import QMovie
from PyQt5.QtWidgets import QSplashScreen
from func import resource_path


class PreLoader(QSplashScreen):
    def __init__(self, *args, **kwargs):
        super(PreLoader, self).__init__(*args, **kwargs)
        self.movie = QMovie(resource_path('img/loader.gif'))
        self.movie.frameChanged.connect(self.onFrameChanged)
        self.movie.start()
        self.setWindowFlags(Qt.WindowStaysOnTopHint)

    def onFrameChanged(self, _):
        self.setPixmap(self.movie.currentPixmap())

    def finish(self, widget):
        self.movie.stop()
        super(PreLoader, self).finish(widget)
