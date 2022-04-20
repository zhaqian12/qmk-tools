from PyQt5.QtCore import QCoreApplication, QSize
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QFileDialog, QDialog,\
     QPlainTextEdit, QSizePolicy, QFrame, QPushButton, QRadioButton, QMessageBox, QGroupBox

import random

from rgb_matrix_generate import RGBMatrixGenerator

tr = QCoreApplication.translate

class RGBGenerator(QWidget):

    def __init__(self):
        super().__init__()

        self.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
        self.vlayout1 = QVBoxLayout()
        self.vlayout2 = QVBoxLayout()
        
        self.hlayout1 = QHBoxLayout()

        self.edit = QPlainTextEdit()
        self.edit.setPlaceholderText(tr("RGBGenerator", "请导入或输入键盘矩阵的json文件(例:via.json的keymap部分)."))
        self.hlayout1.addWidget(self.edit)

        self.vlayout3 = QVBoxLayout()
        self.groupbox1 = QGroupBox(tr("RGBGenerator", "灯位"))
        self.rbtn_up = QRadioButton()
        self.rbtn_up.setText(tr("RGBGenerator", "上灯位"))
        self.vlayout3.addWidget(self.rbtn_up)
        self.rbtn_up.toggled.connect(lambda :self.rbtn_group1_state(self.rbtn_up))
        self.rbtn_down = QRadioButton()
        self.rbtn_down.setText(tr("RGBGenerator", "下灯位"))
        self.vlayout3.addWidget(self.rbtn_down)
        self.rbtn_down.toggled.connect(lambda :self.rbtn_group1_state(self.rbtn_down))
        self.groupbox1.setLayout(self.vlayout3)
        self.vlayout2.addWidget(self.groupbox1)

        self.groupbox2 = QGroupBox(tr("RGBGenerator", "灯珠连接顺序"))
        self.vlayout4 = QVBoxLayout()

        self.rbtn_lr = QRadioButton()
        self.rbtn_lr.setText(tr("RGBGenerator", "从左往右"))
        self.vlayout4.addWidget(self.rbtn_lr)
        self.rbtn_lr.toggled.connect(lambda :self.rbtn_group2_state(self.rbtn_lr))

        self.rbtn_rl = QRadioButton()
        self.rbtn_rl.setText(tr("RGBGenerator", "从右往左"))
        self.vlayout4.addWidget(self.rbtn_rl)
        self.rbtn_rl.toggled.connect(lambda :self.rbtn_group2_state(self.rbtn_rl))

        self.rbtn_s = QRadioButton()
        self.rbtn_s.setText(tr("RGBGenerator", "S形顺序"))
        self.vlayout4.addWidget(self.rbtn_s)
        self.rbtn_s.toggled.connect(lambda :self.rbtn_group2_state(self.rbtn_s))

        self.rbtn_cs = QRadioButton()
        self.rbtn_cs.setText(tr("RGBGenerator", "反S形顺序"))
        self.vlayout4.addWidget(self.rbtn_cs)
        self.rbtn_cs.toggled.connect(lambda :self.rbtn_group2_state(self.rbtn_cs))
        self.groupbox2.setLayout(self.vlayout4)
        self.vlayout2.addWidget(self.groupbox2)

        self.line1 = QFrame()
        self.line1.setFrameShape(QFrame.VLine)
        self.line1.setFrameShadow(QFrame.Sunken)
        self.hlayout1.addWidget(self.line1)
        self.hlayout1.addLayout(self.vlayout2)

        self.vlayout1.addLayout(self.hlayout1)

        self.line2 = QFrame()
        self.line2.setFrameShape(QFrame.HLine)
        self.line2.setFrameShadow(QFrame.Sunken)
        self.vlayout1.addWidget(self.line2)

        self.hlayout2 = QHBoxLayout()

        self.btn_import = QPushButton()
        sizePolicy = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btn_import.sizePolicy().hasHeightForWidth())
        self.btn_import.setSizePolicy(sizePolicy)
        self.btn_import.setMinimumSize(QSize(0, 30))
        self.btn_import.setText(tr("RGBGenerator", "导入json"))
        self.hlayout2.addWidget(self.btn_import)
        self.btn_import.clicked.connect(self.import_json)

        self.btn_generate = QPushButton()
        sizePolicy.setHeightForWidth(self.btn_generate.sizePolicy().hasHeightForWidth())
        self.btn_generate.setSizePolicy(sizePolicy)
        self.btn_generate.setMinimumSize(QSize(0, 30))
        self.btn_generate.setText(tr("RGBGenerator", "生成RGB矩阵"))
        self.hlayout2.addWidget(self.btn_generate)
        self.btn_generate.clicked.connect(self.generate_matrix)

        self.vlayout1.addLayout(self.hlayout2)
        self.setLayout(self.vlayout1)

        self.rbtn_up.setChecked(True)
        self.rbtn_lr.setChecked(True)
        self.led_pos = 0
        self.led_seq = 0
        self.generator = RGBMatrixGenerator()

    def rbtn_group1_state(self, rbtn):
        if rbtn.text() == "上灯位":
            if rbtn.isChecked()==True:
                self.led_pos = 0
            else:
                self.led_pos = 1

        if rbtn.text() == "下灯位":
            if rbtn.isChecked() == True:
                self.led_pos = 1
            else:
                self.led_pos = 0

    def rbtn_group2_state(self, rbtn):
        if rbtn.text() == "从左往右":
            if rbtn.isChecked()==True:
                self.led_seq = 0
        elif rbtn.text() == "从右往左":
            if rbtn.isChecked()==True:
                self.led_seq = 1
        elif rbtn.text() == "S形顺序":
            if rbtn.isChecked()==True:
                self.led_seq = 2
        elif rbtn.text() == "反S形顺序":
            if rbtn.isChecked()==True:
                self.led_seq = 3
        

    def import_json(self):
        dialog = QFileDialog()
        dialog.setDefaultSuffix("json")
        dialog.setAcceptMode(QFileDialog.AcceptOpen)
        dialog.setNameFilters(["layout JSON (*.json)"])
        if dialog.exec_() == QDialog.Accepted:
            with open(dialog.selectedFiles()[0], 'rb') as inf:
                data = inf.read()
            self.edit.setPlainText(data.decode("utf-8-sig"))


    def generate_matrix(self):
        data = self.edit.toPlainText()
        try:
            result = self.generator.generate_matrix(data, self.led_pos, self.led_seq)
        except(Exception):
            QMessageBox.warning(self, "QMK Tools", "生成矩阵失败,请检查json是否正确", QMessageBox.Yes)
            return
        ran = random.randint(0, 10000)
        with open("generator{}.c".format(ran),'w') as fp:
            fp.writelines(result)
        fp.close()
        reply = QMessageBox.information(self, "QMK Tools","已在'generator{}.c'中生成rgb矩阵代码,\n是否在文本框中显示?".format(ran), QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.edit.setPlainText("".join(result))



