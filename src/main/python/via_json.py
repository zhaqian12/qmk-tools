# Based on https://github.com/DamSenViet/kle-py

from PyQt5 import QtCore
from PyQt5.QtCore import QCoreApplication
from PyQt5.QtWidgets import QWidget, QPushButton, QHBoxLayout, QSizePolicy,\
     QVBoxLayout, QPlainTextEdit, QFrame, QFileDialog, QDialog, QMessageBox

import json
from typing import TypeVar, Union, Tuple, List, Dict

tr = QCoreApplication.translate
T = TypeVar("T")
S = TypeVar("S")

json_dump_options = {
    "skipkeys": False,
    "ensure_ascii": True,
    "check_circular": True,
    "allow_nan": True,
    "cls": None,
    "indent": 2,
    "separators": None,
    "default": None,
    "sort_keys": False,
}


class JKey:
     def __init__(self):
        self.label = ""
        self.row = 0
        self.col = 0
        self.x = 0
        self.y = 0
        self.width = 1
        self.height = 1
        self.x2 = 0
        self.y2 = 0
        self.width2 = 1
        self.height2 = 1
        self.rotation_x = 0
        self.rotation_y = 0
        self.rotation_angle = 0


class JKeyboard:
    def __init__(self):
        self.name = ""
        self.vid = "0xFEED"
        self.pid = "0x6060"
        self.rows = self.cols = 0
        self.keys = []


class ViaGenerator(QWidget):
    
    def __init__(self):
        super().__init__()
        
        self.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
        self.vlayout = QVBoxLayout()

        self.edit = QPlainTextEdit()
        self.edit.setPlaceholderText(tr("ViaGenerator", "请导入或输入Keyboard Firmware Builder生成的配置json."))
        self.vlayout.addWidget(self.edit)

        self.line = QFrame()
        self.line.setFrameShape(QFrame.HLine)
        self.line.setFrameShadow(QFrame.Sunken)
        self.vlayout.addWidget(self.line)
        
        self.hlayout = QHBoxLayout()

        self.btn_import = QPushButton()
        sizePolicy = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btn_import.sizePolicy().hasHeightForWidth())
        self.btn_import.setSizePolicy(sizePolicy)
        self.btn_import.setMinimumSize(QtCore.QSize(0, 30))
        self.btn_import.setText(tr("ViaGenerator", "导入json"))
        self.hlayout.addWidget(self.btn_import)
        self.btn_import.clicked.connect(self.import_json)

        self.btn_generate = QPushButton()
        sizePolicy.setHeightForWidth(self.btn_generate.sizePolicy().hasHeightForWidth())
        self.btn_generate.setSizePolicy(sizePolicy)
        self.btn_generate.setMinimumSize(QtCore.QSize(0, 30))
        self.btn_generate.setText(tr("ViaGenerator", "生成via json"))
        self.hlayout.addWidget(self.btn_generate)
        self.btn_generate.clicked.connect(self.generate_json)

        self.vlayout.addLayout(self.hlayout)
        self.setLayout(self.vlayout)

    
    def _key_sort_criteria(self, key: JKey) -> Tuple[float, float, float, float, float]:
        return ((key.rotation_angle + 360) % 360, key.rotation_x, key.rotation_y, key.y, key.x)
    

    def _aligned_key_properties(self, key: JKey) -> Tuple[str]:
        text = key.label
        if text != "":
            aligned_text_labels = text
        return aligned_text_labels


    def _record_change(self, changes: Dict, name: str, val: T, default_val: S) -> T:
        if val != default_val:
            if type(val) is float:
                if val % 1.0 == 0.0:
                    changes[name] = int(val)
                else:
                    changes[name] = val
            else:
                changes[name] = val
        return val


    def import_json(self):
        dialog = QFileDialog()
        dialog.setDefaultSuffix("json")
        dialog.setAcceptMode(QFileDialog.AcceptOpen)
        dialog.setNameFilters(["layout JSON (*.json)"])
        if dialog.exec_() == QDialog.Accepted:
            self.file = dialog.selectedFiles()[0]
            with open(dialog.selectedFiles()[0], "rb") as inf:
                data = inf.read()
            self.edit.setPlainText(data.decode("utf-8-sig"))
    

    def generate_json(self):
        data = self.edit.toPlainText()
        build_json = json.loads(data)
        kb = self.get_keyboard_info(build_json)
        kbjs = self.generate_keymap_json(kb)
        self.generate_via_json(kb, kbjs)


    def get_keyboard_info(self, json):
        kb = JKeyboard()    
        kb.name = json["keyboard"]["settings"]["name"]
        kb.rows = json["keyboard"]["rows"]
        kb.cols = json["keyboard"]["cols"]
        keys = json["keyboard"]["keys"]
        for key in keys:
            tmp = JKey()
            tmp.row = key["row"]
            tmp.col = key["col"]
            tmp.x = key["state"]["x"]
            tmp.y = key["state"]["y"]
            tmp.width = key["state"]["w"]
            tmp.height = key["state"]["h"]
            tmp.x2 = key["state"]["x2"]
            tmp.y2 = key["state"]["y2"]
            tmp.width2 = key["state"]["w2"]
            tmp.height2 = key["state"]["h2"]
            tmp.rotation_x = key["state"]["rx"]
            tmp.rotation_y = key["state"]["ry"]
            tmp.rotation_angle = key["state"]["r"]
            tmp.label = "{r},{c}".format(r = tmp.row, c = tmp.col)
            kb.keys.append(tmp)
        return kb


    def generate_keymap_json(self, kb):
        cluster_rotation_angle: float = 0.0
        cluster_rotation_x: float = 0.0
        cluster_rotation_y: float = 0.0 
        current : JKey = JKey()
        keyboard_json : List[Union[Dict, List[Union[str, Dict]]]] = list()
        row: List[Union[str, Dict]] = list()
        is_new_row: bool = True
        current.y -= 1.0
        sorted_keys: List[JKey] = list(sorted(kb.keys, key=self._key_sort_criteria))
        for key in sorted_keys:
            key_changes = dict()
            aligned_text_labels = self._aligned_key_properties(key)
            is_cluster_changed: bool = ((key.rotation_angle != cluster_rotation_angle) or (key.rotation_x != cluster_rotation_x)
                                    or (key.rotation_y != cluster_rotation_y))
            is_row_changed: bool = key.y != current.y
            if len(row) > 0 and (is_row_changed or is_cluster_changed):
                keyboard_json.append(row)
                row = list()
                is_new_row = True
            if is_new_row:
                current.y += 1.0
                if (
                    key.rotation_y != cluster_rotation_y
                    or key.rotation_x != cluster_rotation_x
                ):
                    current.y = key.rotation_y
                current.x = key.rotation_x
                cluster_rotation_angle = key.rotation_angle
                cluster_rotation_x = key.rotation_x
                cluster_rotation_y = key.rotation_y
                is_new_row = False
            current.rotation_angle = self._record_change(key_changes, "r", key.rotation_angle, current.rotation_angle)
            current.rotation_x = self._record_change(key_changes, "rx", key.rotation_x, current.rotation_x)
            current.rotation_y = self._record_change(key_changes,"ry",key.rotation_y,current.rotation_y)
            current.y += self._record_change(key_changes, "y", key.y - current.y, 0.0)
            current.x += (self._record_change(key_changes, "x", key.x - current.x, 0.0) + key.width)
            self._record_change(key_changes, "w", key.width, 1.0)
            self._record_change(key_changes, "h", key.height, 1.0)
            self._record_change(key_changes, "w2", key.width2, 0.0)
            self._record_change(key_changes, "h2", key.height2, 0.0)
            self._record_change(key_changes, "x2", key.x2, 0.0)
            self._record_change(key_changes, "y2", key.y2, 0.0)
            if len(key_changes) > 0:
                row.append(key_changes)
            row.append(aligned_text_labels.rstrip())
        if len(row) > 0:
            keyboard_json.append(row)
        return keyboard_json


    def generate_via_json(self, kb, kbjs):
        data = {"name" : kb.name, "vendorId" : kb.vid, "productId" : kb.pid, 
                "lighting": "none", "matrix" : {"rows" : kb.rows, "cols" : kb.cols}, 
                "layouts": {"keymap": kbjs}}
        file_name = "{}_via.json".format(kb.name)
        with open(file_name, 'w') as f:   
            json.dump(data, f, **json_dump_options)
        f.close()
        reply = QMessageBox.information(self, "QMK Tools", "已在\'{}\'中生成via json文件,\n是否在文本框中显示?".format(file_name), QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            with open(file_name, 'rb') as f:
                res = f.read().decode("utf-8")
            self.edit.setPlainText(res)
            f.close()
    


