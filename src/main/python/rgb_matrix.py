from PyQt5 import QtCore
from PyQt5.QtCore import QCoreApplication
from PyQt5.QtWidgets import QWidget,  QHBoxLayout, QVBoxLayout, QFileDialog, QDialog,\
     QPlainTextEdit, QSizePolicy, QFrame, QPushButton, QRadioButton, QMessageBox

import json
import random
import copy

from kle_serial import Serial as KleSerial
from collections import OrderedDict
from typing import Tuple

tr = QCoreApplication.translate

strs = [
        "#ifdef RGB_MATRIX_ENABLE \n\n"
        "led_config_t g_led_config = {\n"
        "\t{\n"
] 

class RGBGenerator(QWidget):

    def __init__(self):
        super().__init__()
        
        
        self.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
        self.vlayout = QVBoxLayout()

        self.edit = QPlainTextEdit()
        self.edit.setPlaceholderText(tr("RGBGenerator", "请导入或输入键盘矩阵的json文件(例:via.json的keymap部分)."))
        self.vlayout.addWidget(self.edit)

        self.line = QFrame()
        self.line.setFrameShape(QFrame.HLine)
        self.line.setFrameShadow(QFrame.Sunken)
        self.vlayout.addWidget(self.line)
        
        self.hlayout = QHBoxLayout()

        self.rbtn_up = QRadioButton()
        self.rbtn_up.setText(tr("RGBGenerator", "上灯位"))
        self.hlayout.addWidget(self.rbtn_up)
        self.rbtn_up.toggled.connect(lambda :self.rbtn_state(self.rbtn_up))
        self.rbtn_down = QRadioButton()
        self.rbtn_down.setText(tr("RGBGenerator", "下灯位"))
        self.hlayout.addWidget(self.rbtn_down)
        self.rbtn_down.toggled.connect(lambda :self.rbtn_state(self.rbtn_down))

        self.vline = QFrame()
        self.vline.setFrameShape(QFrame.VLine)
        self.vline.setFrameShadow(QFrame.Sunken)
        self.hlayout.addWidget(self.vline)

        self.btn_import = QPushButton()
        sizePolicy = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btn_import.sizePolicy().hasHeightForWidth())
        self.btn_import.setSizePolicy(sizePolicy)
        self.btn_import.setMinimumSize(QtCore.QSize(0, 30))
        self.btn_import.setText(tr("RGBGenerator", "导入json"))
        self.hlayout.addWidget(self.btn_import)
        self.btn_import.clicked.connect(self.import_json)

        self.btn_generate = QPushButton()
        sizePolicy.setHeightForWidth(self.btn_generate.sizePolicy().hasHeightForWidth())
        self.btn_generate.setSizePolicy(sizePolicy)
        self.btn_generate.setMinimumSize(QtCore.QSize(0, 30))
        self.btn_generate.setText(tr("RGBGenerator", "生成RGB矩阵"))
        self.hlayout.addWidget(self.btn_generate)
        self.btn_generate.clicked.connect(self.generate_matrix)

        self.vlayout.addLayout(self.hlayout)
        self.setLayout(self.vlayout)

        self.rbtn_up.setChecked(True)
        self.light_pos = 0


    def rbtn_state(self, rbtn):
        if rbtn.text() == "上灯位":
            if rbtn.isChecked()==True:
                self.light_pos = 0
            else:
                self.light_pos = 1

        if rbtn.text() == "下灯位":
            if rbtn.isChecked() == True:
                self.light_pos = 1
            else:
                self.light_pos = 0


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
        res = copy.deepcopy(strs)
        n = 0
        data = self.edit.toPlainText()
        matrix_json = json.loads(data)
        serial = KleSerial()
        kb = serial.deserialize(matrix_json)
        (xmax, ymax) = self.get_x_y_max(kb.keys)
        (keys, rc, rowmax, colmax) = self.get_key_row_col(kb)
        
        for r in range(rowmax):
            res.append("\t\t{")
            for c in range(colmax):
                if (rc[r * colmax + c] == True):
                    if (c == (colmax - 1)):
                        res.append("{}".format(n) + "},\n" )
                    else:
                        res.append("{}, ".format(n))
                    n += 1
                else:
                    if (c == (colmax - 1)):
                        res.append("NO_LED" + "},\n")
                    else:
                        res.append("NO_LED" + ", ")
        res.append("\t}, {\n")

        n = -1
        for key in keys:
            if (key.row != n):
                if key.row != 0:
                    res.append("\n")
                n = key.row
                res.append("\t\t")
            x = round((key.x + key.width / 2.0) / xmax * 224.0)
            y = 0
            if self.light_pos == 0:
                y = round((key.y + key.height / 5.0 * 1.2) / ymax * 64.0)
            else:
                y = round((key.y + key.height / 5.0 * 3.8) / ymax * 64.0)
            res.append("{" + "{xx}, {yy}".format(xx = x, yy = y) + "}, ")
        res.append("\n\t}, {\n")

        for key in keys:
            if (key.row != n):
                if key.row != 0:
                    res.append("\n")
                n = key.row
                res.append("\t\t")
            res.append("4, ")
        res.append("\n\t}\n};\n\n#endif\n")
        ran = random.randint(0, 10000)
        with open("generator{}.c".format(ran),'w') as fp:
            fp.writelines(res)
        fp.close()
        reply = QMessageBox.information(self, "QMK Tools","已在'generator{}.c'中生成rgb矩阵代码,\n是否在文本框中显示?".format(ran), QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.edit.setPlainText("".join(res))


    def get_x_y_max(self, keys) -> Tuple[float, float]:
        tmp_x_key = tmp_y_key = 0
        xmax = ymax = 0
        for key in keys:
            if (key.x > xmax):
                xmax = key.x
                tmp_x_key = key
            if (key.y > ymax):
                ymax = key.y
                tmp_y_key = key
        xmax += tmp_x_key.width
        ymax += tmp_y_key.height
        return (xmax, ymax)


    def get_key_row_col(self, kb) -> Tuple[list, list, int, int]:
        rowcol = OrderedDict()
        keys = []
        rc = []
        rowmax = colmax = 0
        for key in kb.keys:
            row, col = 0, 0
            if key.labels[0] and "," in key.labels[0]:
                    row, col = key.labels[0].split(",")
                    row, col = int(row), int(col)
            key.row = row
            key.col = col
            if (row > rowmax):
                rowmax = row
            if (col > colmax):
                colmax = col
            rowcol[(row, col)] = True
            keys.append(key)
        rowmax += 1
        colmax += 1
        for r in range(rowmax * colmax):
            rc.append(False)
        for r, c in rowcol.keys():
            rc[r * colmax + c] = True
        return (keys, rc, rowmax, colmax)