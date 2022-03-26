from PyQt5.QtCore import QSettings, QCoreApplication
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QMainWindow, QAction, QTabWidget, QMessageBox

from via_json import ViaGenerator
from rgb_matrix import RGBGenerator

tr = QCoreApplication.translate

class MainWindow(QMainWindow):

    def __init__(self, appctx):
        super().__init__()
        self.appctx = appctx

        self.settings = QSettings("ZQ", "QMK-Tools")
        if self.settings.value("size", None) and self.settings.value("pos", None):
            self.resize(self.settings.value("size"))
            self.move(self.settings.value("pos"))
        else:
            self.resize(520, 390)

        self.tabs = QTabWidget()
        self.tab_via = ViaGenerator()
        self.tab_rgb = RGBGenerator()
        self.tabs.addTab(self.tab_via, "")
        self.tabs.addTab(self.tab_rgb, "")
        self.tabs.setTabText(self.tabs.indexOf(self.tab_via), tr("MainWindow", "Via json生成"))
        self.tabs.setTabText(self.tabs.indexOf(self.tab_rgb), tr("MainWindow", "QMK RGB Matrix生成"))

        layout = QVBoxLayout()
        layout.addWidget(self.tabs)
        w = QWidget()
        w.setLayout(layout)
        self.setCentralWidget(w)
        help_act = QAction(tr("MenuHelp", "帮助..."), self)
        help_act.triggered.connect(self.help)
        self.help_menu = self.menuBar().addMenu(tr("Menu", "帮助"))
        self.help_menu.addAction(help_act)

        self.tabs.setCurrentIndex(0)


    def help(self):
        QMessageBox.about(
            self,
            "QMK Tools",
            'QMK Tools {}<br><br>'
            '自动生成初始的VIA JSON和QMK RGB MATRIX. <br><br>'
            '使用前请进行检查与修改!!! <br><br>'
            '<a href="https://github.com/zhaqian12/qmk-tools/">https://github.com/zhaqian12/qmk-tools/</a>'
            .format(self.appctx.build_settings["version"])
        )


    def closeEvent(self, e):
        self.settings.setValue("size", self.size())
        self.settings.setValue("pos", self.pos())
        e.accept()
