import json
import copy

from kle_serial import Serial as KleSerial
from collections import OrderedDict
from typing import Tuple

strs = [
        "#ifdef RGB_MATRIX_ENABLE \n\n"
        "led_config_t g_led_config = {\n"
        "\t{\n"
] 

class RGBMatrixGenerator():
    def __init__(self):
        super().__init__()
        self.res = []

    def generate_matrix(self, data, led_pos, led_seq):
        self.res = copy.deepcopy(strs)
        matrix_json = json.loads(data)
        serial = KleSerial()
        kb = serial.deserialize(matrix_json)
        (xmax, ymax) = self.get_x_y_max(kb.keys)
        (keys, rc, rowmax, colmax) = self.get_key_row_col(kb)
        keys = self.sort_led(keys)
        if led_seq == 0:
            self.generate_matrix_map_left_to_right(rowmax, colmax, rc)
            self.generate_matrix_pos_horizontal(keys, led_pos, xmax, ymax, 0)
        elif led_seq == 1:
            self.generate_matrix_map_right_to_left(rowmax, colmax, rc)
            self.generate_matrix_pos_horizontal(keys, led_pos, xmax, ymax, 1)
        elif led_seq == 2:
            self.generate_matrix_map_snake(rowmax, colmax, rc, 0)
            self.generate_matrix_pos_snake(keys, led_pos, xmax, ymax, 0)
        elif led_seq == 3:
            self.generate_matrix_map_snake(rowmax, colmax, rc, 1)
            self.generate_matrix_pos_snake(keys, led_pos, xmax, ymax, 1)
            
        n = -1
        for key in keys:
            if (key.row != n):
                if key.row != 0:
                    self.res.append("\n")
                n = key.row
                self.res.append("\t\t")
            self.res.append("4, ")
        self.res.append("\n\t}\n};\n\n#endif\n")
        
        return self.res


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
    

    def generate_matrix_map_left_to_right(self, rowmax, colmax, rc):
        n = 0
        for r in range(rowmax):
            self.res.append("\t\t{")
            for c in range(colmax):
                if (rc[r * colmax + c] == True):
                    if (c == (colmax - 1)):
                        self.res.append("{}".format(n) + "},\n" )
                    else:
                        self.res.append("{}, ".format(n))
                    n += 1
                else:
                    if (c == (colmax - 1)):
                        self.res.append("NO_LED" + "},\n")
                    else:
                        self.res.append("NO_LED" + ", ")
        self.res.append("\t}, {\n")

    
    def generate_matrix_map_right_to_left(self, rowmax, colmax, rc):
        n = 0
        row_led_num = self.get_row_led_num(rowmax, colmax, rc)

        for r in range(rowmax):
            self.res.append("\t\t{")
            n = row_led_num[r] - 1
            for c in range(colmax):
                if (rc[r * colmax + c] == True):
                    if (c == (colmax - 1)):
                        self.res.append("{}".format(n) + "},\n" )
                    else:
                        self.res.append("{}, ".format(n))
                    n -= 1
                else:
                    if (c == (colmax - 1)):
                        self.res.append("NO_LED" + "},\n")
                    else:
                        self.res.append("NO_LED" + ", ")
        self.res.append("\t}, {\n")


    def generate_matrix_map_snake(self, rowmax, colmax, rc, counter):
        n = 0
        row_led_num = self.get_row_led_num(rowmax, colmax, rc)
        for r in range(rowmax):
            self.res.append("\t\t{")
            if r % 2 == 0:
                if counter == 0:
                    n = row_led_num[r] - 1
                else:
                    if r != 0:
                        n = row_led_num[r - 1]
            else:
                if counter == 0:
                    n = row_led_num[r - 1]
                else:
                    n = row_led_num[r] - 1
            for c in range(colmax):
                if (rc[r * colmax + c] == True):
                    if (c == (colmax - 1)):
                        self.res.append("{}".format(n) + "},\n" )
                    else:
                        self.res.append("{}, ".format(n))
                    if r % 2 == 0:
                        if counter == 0:
                            n -= 1
                        else: 
                            n += 1
                    else:
                        if counter == 0:
                            n += 1
                        else: 
                            n -= 1
                else:
                    if (c == (colmax - 1)):
                        self.res.append("NO_LED" + "},\n")
                    else:
                        self.res.append("NO_LED" + ", ")
        self.res.append("\t}, {\n")


    def get_row_led_num(self, rowmax, colmax, rc):
        n = 0
        row_led_num = []
        for r in range(rowmax):
            for c in range(colmax):
                if (rc[r * colmax + c] == True):
                    n += 1
            row_led_num.append(n)
        return row_led_num


    def generate_matrix_pos_horizontal(self, keys, led_pos, xmax, ymax, counter):
        n = -1
        tmp = []
        for key in keys:
            if (key.row != n):
                self.append_result(counter, tmp, 1)
                tmp.clear()
                if key.row != 0:
                    self.res.append("\n")
                n = key.row
                self.res.append("\t\t")
            x = round((key.x + key.width / 2.0) / xmax * 224.0)
            y = 0
            if led_pos == 0:
                y = round((key.y + key.height / 5.0 * 1.2) / ymax * 64.0)
            else:
                y = round((key.y + key.height / 5.0 * 3.8) / ymax * 64.0)
            tmp.append("{" + "{xx}, {yy}".format(xx = x, yy = y) + "}, ")

        if len(tmp):
            self.append_result(counter, tmp, 1)
        self.res.append("\n\t}, {\n")


    def generate_matrix_pos_snake(self, keys, led_pos, xmax, ymax, counter):
        n = -1
        tmp = []
        for key in keys:
            if (key.row != n):
                n = key.row
                self.append_result(counter, tmp, n)
                tmp.clear()
                if key.row != 0:
                    self.res.append("\n")
                self.res.append("\t\t")
            x = round((key.x + key.width / 2.0) / xmax * 224.0)
            y = 0
            if led_pos == 0:
                y = round((key.y + key.height / 5.0 * 1.2) / ymax * 64.0)
            else:
                y = round((key.y + key.height / 5.0 * 3.8) / ymax * 64.0)
            tmp.append("{" + "{xx}, {yy}".format(xx = x, yy = y) + "}, ")
        
        if len(tmp):
            self.append_result(counter, tmp, n)
        self.res.append("\n\t}, {\n")


    def append_result(self, counter, tmp, n):
        if n % 2 == 0:
            if counter == 0:
                for ele in reversed(tmp):
                    self.res.append(ele)
            else :
                for ele in tmp:
                    self.res.append(ele)
        else :
            if counter == 1:
                for ele in reversed(tmp):
                    self.res.append(ele)
            else :
                for ele in tmp:
                    self.res.append(ele)

    def sort_led(self, keys):
        n = 0
        tmprow = tmpcol = 0
        for key in keys:
            if (tmprow != key.row):
                tmprow = key.row
                tmpcol = 0
            if (tmpcol > key.col):
                keys[n-1],keys[n] = keys[n],keys[n-1]
            tmpcol = key.col
            n += 1
        return keys