import sys
import re
from stack import Stack
from decimal import Decimal
from PyQt5.QtWidgets import QApplication, QWidget, QGridLayout, QPushButton, QLineEdit, QVBoxLayout
from PyQt5.QtGui import QFont, QCursor, QIcon
from PyQt5.QtCore import Qt
import resource

class Calc(QWidget):
    count_left_bracket = 0
    dot_lock_flag = False

    def __init__(self):
        super(Calc, self).__init__()
        self.init_gui()

    def init_gui(self):
        self.calc_height = 360
        self.calc_width = 380
        self.setFixedSize(self.calc_width, self.calc_height)
        self.setWindowTitle("计算器 by Violet")
        self.setWindowIcon(QIcon(":/icon.png"))
        self.setStyleSheet("background-color:rgb(252,253,255)")

        self.process_textline = QLineEdit("")
        self.process_textline.setAlignment(Qt.AlignRight)
        self.process_textline.setReadOnly(True)
        self.process_textline.setFont(QFont("华文琥珀", 16, QFont.Light))
        self.process_textline.setStyleSheet("border:none")

        self.answer_textline = QLineEdit("")
        self.answer_textline.setAlignment(Qt.AlignRight)
        self.answer_textline.setReadOnly(True)
        self.answer_textline.setFont(QFont("华文琥珀", 20, QFont.Bold))
        self.answer_textline.setStyleSheet("border:none")

        wdg = QWidget(self)

        outer_vbox = QVBoxLayout(wdg)
        outer_vbox
        vbox = QVBoxLayout()
        vbox.addWidget(self.process_textline)
        vbox.addWidget(self.answer_textline)
        vbox.setContentsMargins(0,0,0,20)

        grid = QGridLayout()
        grid.setSpacing(0)

        btn_names = ['(', ')', '', 'C',
                 '7', '8', '9', '/',
                 '4', '5', '6', 'x',
                 '1', '2', '3', '-',
                 '0', '.', '=', '+']

        positions = [(i, j) for i in range(1, 6) for j in range(4)]

        index = 0
        color_symbol = (1,2,8,12,16,18,19,20)
        for position, name in zip(positions, btn_names):
            index += 1
            if name == '':
                continue
            btn = QPushButton(name)

            if index in color_symbol:
                btn.setStyleSheet("QPushButton{font-size:16px; font-family:SimHei; border:1px solid rgb(235,235,235); color:rgb(255,102,0)}"
                                  "QPushButton:hover{background-color:rgb(243,243,243)} QPushButton:pressed{background-color:rgb(233,233,233)}")
            else:
                btn.setStyleSheet("QPushButton{font-size:16px; font-family:SimHei; border:1px solid rgb(235,235,235); color:rgb(51,51,51)}"
                                  "QPushButton:hover{background-color:rgb(243,243,243)} QPushButton:pressed{background-color:rgb(233,233,233)}")
            btn.setCursor(QCursor(Qt.PointingHandCursor))
            btn.setFixedSize(90, 50)
            btn.clicked.connect(self.button_clicked)

            grid.addWidget(btn, *position)


        outer_vbox.addLayout(vbox)
        outer_vbox.addLayout(grid)

    def button_clicked(self):
        clicked_symbol = self.sender().text()

        if self.answer_textline.text() == '∞' or self.answer_textline.text() == "something went wrong" or self.answer_textline.text() == "excess limit" or self.answer_textline.text() == "error":
            self.answer_textline.setText('')

        # 小数点自动补零
        if clicked_symbol == '.' and not self.dot_lock_flag:
            if self.answer_textline.text() == '' or (not self.answer_textline.text()[-1].isdigit() and self.answer_textline.text()[-1] != ')' and self.answer_textline.text()[-1] != '.'):
                self.answer_textline.setText(self.answer_textline.text() + "0.")
                self.dot_lock_flag = True

        #进行符号限制
        if not self.can_add_symbol(self.answer_textline.text(), clicked_symbol):
            return

        expression = self.answer_textline.text() + clicked_symbol

        if clicked_symbol == '=':
            #去掉无用符号尾巴，碰到')'和数字停止
            try:
                while expression[-2] != ')' and not expression[-2].isdigit():
                    if expression[-2] == '(':
                        self.count_left_bracket -= 1
                    expression = expression[:-2] + expression[-1]
            except Exception:
                self.process_textline.setText('=')
                self.answer_textline.setText('error')
                return

            #append all of right brackets if it has remain
            if self.count_left_bracket > 0:
                expression_list = list(expression)

                while self.count_left_bracket > 0:
                    expression_list.insert(-1, ')')
                    self.count_left_bracket -= 1

                expression = ''.join(expression_list)

            self.process_textline.setText(expression)

            #calculate the result
            #get_rear_expression() get calculation result directly, it does not means get the rear expression, the whole
            #             process is moving in get_rear_expression func
            self.answer_textline.setText(self.get_rear_expression(expression[:-1]))
            self.count_left_bracket = 0

        elif clicked_symbol == 'C':
            self.process_textline.setText('')
            self.answer_textline.setText('')
            self.dot_lock_flag = False

            self.count_left_bracket = 0
        else:
            self.answer_textline.setText(expression)


    def get_rear_expression(self, mid_expression):
        nums_list = list(filter(None, re.split(r"[+\-x/()]",mid_expression)))

        nums_p_n_list = ["p"] * len(nums_list)
        self.set_p_n(mid_expression, mid_expression[0], nums_p_n_list)

        '''
        #ver1.0
        #Reason to note: i moved this process to next level, notice at func: set_p_n()
        #date: 2020-1-30 12:47
        
        first_is_n_flag = False
        #第一个负号为数
        if mid_expression[0] == '-':
            self.nums_p_n_list[0] = 'n'
            first_is_n_flag = True
        #负号的左右两边如果有运算符则为负号
        if first_is_n_flag:
            self.set_p_n(mid_expression[1:], 1)
        else:
            self.set_p_n(mid_expression, 0)
        '''

        nums_list_index = 0

        symbol_stack = Stack()
        rear_expression_stack = Stack()
        num_inside_flag = False

        char_index = -1
        for char in mid_expression:
            char_index += 1
            #运算符'-'是要记入后缀表达式，而表示负号的'-'则直接跳过
            if char.isdigit():
                if num_inside_flag:
                    continue

                rear_expression_stack.push(nums_list[nums_list_index])
                num_inside_flag = True
                nums_list_index += 1
                continue

            if char == '.':
                continue

            #负号的跳过
            if char == '-' and (char_index == 0 or (not mid_expression[char_index - 1].isdigit() and mid_expression[char_index - 1] != ')')):
                continue

            num_inside_flag = False

            if char == '(':
                symbol_stack.push(char)
                continue

            if char == ')':
                while symbol_stack.peek() != '(':
                    rear_expression_stack.push(symbol_stack.pop())

                symbol_stack.pop()
                continue

            if symbol_stack.len() > 0:
                while self.get_symbol_level(char) <= self.get_symbol_level(symbol_stack.peek()):
                    #pop
                    rear_expression_stack.push(symbol_stack.pop())

                    if symbol_stack.len() == 0:
                        break

            symbol_stack.push(char)

        while symbol_stack.len() > 0:
            rear_expression_stack.push(symbol_stack.pop())

        return self.calc_rear_expression(rear_expression_stack, nums_p_n_list)


    def set_p_n(self, str, start, nums_p_n_list):
        #任何符号后面一位为数字则定义为下一位数
        #如果符号为'-'满足上面条件，判断该'-'左右两边是否均为数字，如成立则为运算符，否则为负号符
        scan_index = 0
        num_index = 0

        #第一种：第一位字符为'-'
        #第二种：第一位不为'-'

        if start == '-':
            nums_p_n_list[num_index] = 'n'
            scan_index += 1
        elif not start.isdigit():
            num_index -= 1

        for char in str[1:] if start == '-' else str:
            if not char.isdigit() and (str[scan_index + 1].isdigit() if scan_index < len(str) - 1 else False) and char != '.':
                num_index += 1

                if char == '-':
                    if not str[scan_index - 1].isdigit() and str[scan_index - 1] != ')':
                        nums_p_n_list[num_index] = 'n'

            scan_index += 1

        # -1-2x(-1+8) 测试数据通过
        # -126x(-9+20) 测试数据通过
        # 174/((-2x-44)) 测试数据通过
        # (8)-2 测试数据通过
        # -(8)-2 测试数据通过
        # 2x(-10+3/-3+1x16x2) 测试数据通过
        # -2x(-10+3/-3+1x16x2)/0 测试数据通过
        # ((((8x2/4-1/2)))) 测试数据通过
        # ((((8x2/4-1/2 测试数据通过
        # 0.075+(((2x3+5/-5))) 测试数据通过
        # (((8+6)x(-            -> (((8+6)))    测试数据通过
        # (((8+6)x(-2           -> (((8+6)x(-2)))   测试数据通过
        # (88)+((((2x3/-2)+-    -> (88)+((((2x3/-2)))) 测试数据通过
        # ((-   能对错误表达式进行捕捉
        # 01+02 测试数据通过

    def calc_rear_expression(self, rear_expression_stack, nums_p_n_list):
        res_stack = Stack()
        nums_index = 0

        try:
            for char in rear_expression_stack.convert_to_list():
                if char.isdigit() or self.is_float(char):
                    res_stack.push(-Decimal(char) if nums_p_n_list[nums_index] == 'n' else Decimal(char))
                    nums_index += 1
                else:
                    num2 = res_stack.pop()
                    num1 = res_stack.pop()

                    tmp = 0

                    if char == 'x':
                        tmp = Decimal(num1) * Decimal(num2)

                    if char == '/':
                        tmp = Decimal(num1) / Decimal(num2)

                    if char == '+':
                        tmp = Decimal(num1) + Decimal(num2)

                    if char == '-':
                        tmp = Decimal(num1) - Decimal(num2)

                    res_stack.push(tmp)
        except ZeroDivisionError:
            return ('∞')
        except Exception:
            return ("program went wrong")

        try:
            if res_stack.peek() == 0 or res_stack.peek() == '0':
                calc_res = '0'
            else:
                calc_res = self.hanle_res_format(round(res_stack.pop(), 10))

            if self.is_float(calc_res):
                self.dot_lock_flag = True
            else:
                self.dot_lock_flag = False

        except Exception:
            return ("excess limit")

        return calc_res

    def get_symbol_level(self, symbol):
        if symbol == 'x' or symbol == '/':
            return 3

        if symbol == '+' or symbol == '-':
            return 2

        if symbol == '(' or symbol == ')':
            return 1

    #reference: https://www.cnblogs.com/xiehong/p/8963635.html
    def is_float(self, num):
        s = str(num)

        if s.count(".") == 1:  # 小数点个数
            s_list = s.split(".")
            left = s_list[0]  # 小数点左边
            right = s_list[1]  # 小数点右边
            if left.isdigit() and right.isdigit():
                return True
            elif left.startswith('-') and left.count('_') == 1 and left.split('-')[1].isdigit() and right.isdigit():
                return True
        return False

    def hanle_res_format(self, num):
        num_str = str(num).rstrip('0')
        return num_str[:-1] if num_str.endswith('.') else num_str

    def can_add_symbol(self, expression, add_symbol):
        if add_symbol == '-':
            if expression.endswith('-'):
                return False
            self.dot_lock_flag = False

        elif add_symbol == '(':
            if expression != '':
                if expression[-1].isdigit() or expression[-1] == ')':
                    return False

            self.count_left_bracket += 1

        elif add_symbol == ')':
            if self.count_left_bracket <= 0 or expression[-1] == '(':
                return False

            self.count_left_bracket -= 1

        elif add_symbol == '+' or add_symbol == 'x' or add_symbol == '/':
            if expression.endswith('+') or expression.endswith('(') or expression.endswith('x') or expression.endswith('/') or expression.endswith('-'):
                return False

            self.dot_lock_flag = False

        elif add_symbol == '.':
            if expression.endswith('.') or expression.endswith(')') or self.dot_lock_flag:
                return False

            self.dot_lock_flag = True

        elif add_symbol.isdigit():
            if expression.endswith(')'):
                return False

        return True

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Calc()
    ex.show()
    sys.exit(app.exec_())