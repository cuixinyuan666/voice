'''
Sidekick
Copyright (C) 2021 UT-Battelle - Created by Sean Oesch

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''
from actions import *
import string


class CommandParser:
    def __init__(self, steps):
        self.steps = steps 
        self.tempvar = ""

        self.keys = ['a', 'b', 'c', 'd', 'e','f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o',
'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z','alt','delete','control','shift','tab']

        self.keymapping = {
            "control" : "ctrl"
        }

        self.grid_horizontal = ['a','b','c','d','e','f','g','h','i','j','k']

        self.grid_vertical = [
            "one",
            "two",
            "three",
            "four",
            "five",
            "six",
            "seven",
            "eight",
            "nine",
            "ten",
            "eleven",
        ]
        self.numbers = [
            "pod",
            "pup",
            "one",
            "two",
            "three",
            "four",
            "five",
            "six",
            "seven",
            "eight",
            "nine",
            "ten",
            "eleven",
            "twelve",
            "thirteen",
            "fourteen",
            "fifteen",
            "sixteen",
            "seventeen",
            "eighteen",
            "nineteen",
            "twenty",
            "thirty",
            "forty",
            "fifty",
            "hundred",
        ]
        self.stateless_commands = [
            "点击",
            "开始",
            "制表",
            "双击",
            "回车",
            "空格",
            "删除",
        ]
        self.commands = [
            "撤销",
            "热键",
            "确认",
            "左移",
            "右移",
            "切换",
            "取消",
            "按键",
            "下一个",
            "重做",
            "关闭",
            "查找",
            "替换",
            "新建",
            "恢复",
            "上一个",
            "下一个",
            "退出",
            "放大",
            "缩小",
            "右键",
            "按住",
            "锁定",
            "终止",
            "释放",
            "三击",
            "网格",
            "上",
            "下",
            "左",
            "右",
            "复制",
            "粘贴",
            "北",
            "南",
            "东",
            "西",
            "保存",
            "滚动",
        ]

        self.commandlist = (
            self.keys
            + self.grid_vertical
            + self.stateless_commands
            + self.commands
            + self.numbers
        )

    def word_to_int(self, word):
        mapping = {
            "one": "1",
            "two": "2",
            "three": "3",
            "four": "4",
            "five": "5",
            "six": "6",
            "seven": "7",
            "eight": "8",
            "nine": "9",
            "ten": "10",
            "eleven": "11",
            "twelve": "12",
            "thirteen": "13",
            "fourteen": "14",
            "fifteen": "15",
            "sixteen": "16",
            "seventeen": "17",
            "eighteen": "18",
            "nineteen": "19",
            "twenty": "20",
            "thirty": "30", 
            "forty": "40",
            "fifty": "50",
            "hundred": "100",
        }
        return mapping[word]

    # Maps key commands to actual button press
    def map_keys(self,val):
        if val in self.keymapping:
            return self.keymapping[val]
        else:
            return val

    # Stateless commands should return an empty buffer
    def stateless_command(self, command_buffer):
        if command_buffer[0] == "点击" or command_buffer[0] == "开始":
            click()
            command_buffer = []
        elif command_buffer[0] == "双击":
            doubleclick()
            command_buffer = []
        elif command_buffer[0] == "回车":
            hitEnter()
            command_buffer = []
        elif command_buffer[0] == "制表":
            hitTab()
            command_buffer = []
        elif command_buffer[0] == "空格":
            hitSpace()
            command_buffer = []
        elif command_buffer[0] == "确认":
            holdKeyDown("alt")
            click()
            keyUp("alt")
            command_buffer = []
        elif command_buffer[0] == "删除":
            if len(command_buffer) >= 2:
                if command_buffer[1] in self.numbers:
                    backspace(int(self.word_to_int(command_buffer[1])))
                    command_buffer = []
                else:
                    return [
                        True,
                        self.handle_invalid_command(command_buffer[1], command_buffer),
                    ]
        else:
            return [False, command_buffer]

        return [True, command_buffer]

    def handle_invalid_command(self, val, command_buffer):
        if val in self.commands or val in self.stateless_commands:
            command_buffer = [val]
            stateless, command_buffer = self.stateless_command(command_buffer)
            if not stateless:
                command_buffer = self.evaluate_command(command_buffer)
        else:
            command_buffer = []

        return command_buffer

    def evaluate_command(self, command_buffer):
        if command_buffer[0] == "右键":
            rightclick()
            command_buffer = []
        elif command_buffer[0] == "左移":
            hotKeyPress(["alt", "left"])
            command_buffer = []
        elif command_buffer[0] == "右移":
            hotKeyPress(["alt", "right"])
            command_buffer = []
        elif command_buffer[0] == "下一页":
            hotKeyPress(["pgdn"])
            command_buffer = []
        elif command_buffer[0] == "上一页":
            hotKeyPress(["pgup"])
            command_buffer = []
        elif command_buffer[0] == "三击":
            tripleclick()
            command_buffer = []
        elif command_buffer[0] == "锁定":
            if len(command_buffer) == 1:
                self.x, self.y = getPosition()
            elif len(command_buffer) >= 2:
                if command_buffer[1] == "释放":
                    dragMouse(self.x, self.y)
                    command_buffer = []
                else:
                    return self.handle_invalid_command(
                        command_buffer[1], command_buffer
                    )
        elif command_buffer[0] == "上":
            if len(command_buffer) >= 2:
                if command_buffer[1] in self.numbers:
                    for i in range(int(self.word_to_int(command_buffer[1]))):
                        hotKeyPress(["up"])
                    command_buffer = []
                else:
                    return self.handle_invalid_command(
                        command_buffer[1], command_buffer
                    )
        elif command_buffer[0] == "下":
            if len(command_buffer) >= 2:
                if command_buffer[1] in self.numbers:
                    for i in range(int(self.word_to_int(command_buffer[1]))):
                        hotKeyPress(["down"])
                    command_buffer = []
                else:
                    return self.handle_invalid_command(
                        command_buffer[1], command_buffer
                    )
        elif command_buffer[0] == "左":
            if len(command_buffer) >= 2:
                if command_buffer[1] in self.numbers:
                    for i in range(int(self.word_to_int(command_buffer[1]))):
                        hotKeyPress(["left"])
                    command_buffer = []
                else:
                    return self.handle_invalid_command(
                        command_buffer[1], command_buffer
                    )
        elif command_buffer[0] == "右":
            if len(command_buffer) >= 2:
                if command_buffer[1] in self.numbers:
                    for i in range(int(self.word_to_int(command_buffer[1]))):
                        hotKeyPress(["right"])
                    command_buffer = []
                else:
                    return self.handle_invalid_command(
                        command_buffer[1], command_buffer
                    )
        elif command_buffer[0] == "复制":
            hotKeyPress(["ctrl", "c"])
            command_buffer = []
        elif command_buffer[0] == "放大":
            hotKeyPress(["ctrl", "+"])
            command_buffer = []
        elif command_buffer[0] == "缩小":
            hotKeyPress(["ctrl", "-"])
            command_buffer = []
        elif command_buffer[0] == "粘贴":
            hotKeyPress(["ctrl", "v"])
            command_buffer = []
        elif command_buffer[0] == "关闭":
            hotKeyPress(["ctrl", "w"])
            command_buffer = []
        elif command_buffer[0] == "查找":
            hotKeyPress(["ctrl", "f"])
            command_buffer = []
        elif command_buffer[0] == "撤销":
            hotKeyPress(["ctrl", "z"])
            command_buffer = []
        elif command_buffer[0] == "重做":
            hotKeyPress(["ctrl", "shift","z"])
            command_buffer = []
        elif command_buffer[0] == "替换":
            hotKeyPress(["ctrl", "h"])
            command_buffer = []
        elif command_buffer[0] == "新建":
            hotKeyPress(["ctrl", "t"])
            command_buffer = []
        elif command_buffer[0] == "恢复":
            hotKeyPress(["ctrl","shift","t"])
            command_buffer = []
        elif command_buffer[0] == "上一个":
            hotKeyPress(["ctrl", "shift","tab"])
            command_buffer = []
        elif command_buffer[0] == "下一个":
            hotKeyPress(["ctrl", "tab"])
            command_buffer = []
        elif command_buffer[0] == "退出":
            hotKeyPress(["escape"])
            command_buffer = []
        elif command_buffer[0] == "终止":
            hotKeyPress(["ctrl", "c"])
            command_buffer = []
        elif command_buffer[0] == "保存":
            hotKeyPress(["ctrl", "s"])
            command_buffer = []
        elif command_buffer[0] == "切换":
            holdKeyDown("alt")

            if len(command_buffer) == 1:
                hotKeyPress(["tab"])

            if len(command_buffer) >= 2:
                if command_buffer[1] == "下一个":
                    hotKeyPress(["tab"])
                    command_buffer = ["切换"]
                elif command_buffer[1] == "退出":
                    hotKeyPress(["escape"])
                    keyUp("alt")
                    command_buffer = []                    
                else:
                    keyUp("alt")
                    command_buffer = []

        elif command_buffer[0] == "按住":

            if len(command_buffer) == 1:
                holdLeft()
                command_buffer = ["按住"]
            else:
                releaseLeft()
                command_buffer = []

        elif command_buffer[0] == "按键":

            if len(command_buffer) >= 2:

                if command_buffer[1] in self.keys:
                    if self.tempvar != "":
                        keyUp(self.tempvar)
                    holdKeyDown(self.map_keys(command_buffer[1]))
                    self.tempvar = self.map_keys(command_buffer[1])
                    command_buffer = ["按键"]

                else:
                    keyUp(self.tempvar)
                    self.tempvar = ""

                    command_buffer = []            

        elif command_buffer[0] == "热键":

            if command_buffer[-1] in self.keys or len(command_buffer) == 1:
                pass

            else:
                hot_keys = []
                for val in command_buffer:
                    if val != "热键":
                        hot_keys.append(self.map_keys(val))
                
                hotKeyPress(hot_keys)

                command_buffer = [] 

        elif command_buffer[0] == "北":
            if len(command_buffer) >= 2:
                if command_buffer[1] in self.steps:
                    moveMouse(0, -1 * int(self.steps[command_buffer[1]]))
                    command_buffer = ["北"]
                else:
                    return self.handle_invalid_command(
                        command_buffer[1], command_buffer
                    )
        elif command_buffer[0] == "南":
            if len(command_buffer) >= 2:
                if command_buffer[1] in self.steps:
                    moveMouse(0, int(self.steps[command_buffer[1]]))
                    command_buffer = ["南"]
                else:
                    return self.handle_invalid_command(
                        command_buffer[1], command_buffer
                    )
        elif command_buffer[0] == "东":
            if len(command_buffer) >= 2:
                if command_buffer[1] in self.steps:
                    moveMouse(int(self.steps[command_buffer[1]]), 0)
                    command_buffer = ["东"]
                else:
                    return self.handle_invalid_command(
                        command_buffer[1], command_buffer
                    )
        elif command_buffer[0] == "西":
            if len(command_buffer) >= 2:
                if command_buffer[1] in self.steps:
                    moveMouse(-1 * int(self.steps[command_buffer[1]]), 0)
                    command_buffer = ["西"]
                else:
                    return self.handle_invalid_command(
                        command_buffer[1], command_buffer
                    )
        elif command_buffer[0] == "滚动":
            if len(command_buffer) >= 2:
                if command_buffer[1] in ["上", "下", "左", "右"]:
                    if len(command_buffer) >= 3:
                        if command_buffer[2] in self.steps:
                            if command_buffer[1] == "上":
                                scrollUp(int(self.steps[command_buffer[2]]))
                                command_buffer = ["滚动", "上"]
                            if command_buffer[1] == "下":
                                scrollUp(-1 * int(self.steps[command_buffer[2]]))
                                command_buffer = ["滚动", "下"]
                            if command_buffer[1] == "左":
                                scrollRight(-1 * int(self.steps[command_buffer[2]]))
                                command_buffer = ["滚动", "左"]
                            if command_buffer[1] == "右":
                                scrollRight(int(self.steps[command_buffer[2]]))
                                command_buffer = ["滚动", "右"]
                        else:
                            return self.handle_invalid_command(
                                command_buffer[2], command_buffer
                            )
                else:
                    return self.handle_invalid_command(
                        command_buffer[1], command_buffer
                    )
        elif command_buffer[0] == "网格":
            if len(command_buffer) >= 2:
                if command_buffer[1] in self.grid_horizontal:
                    if len(command_buffer) >= 3:
                        if command_buffer[2] in self.grid_vertical:
                            x, y = screenSize()
                            horizontal = string.ascii_lowercase.index(
                                command_buffer[1]
                            )  # 0 indexed
                            vertical = int(self.word_to_int(command_buffer[2])) - 1
                            xpoint = float(horizontal) * (x / 10.0)
                            ypoint = y - float(vertical) * (y / 10.0)

                            # add some buffer to keep mouse off the very edges of the screen / visible
                            if xpoint == x:
                                xpoint = xpoint - 20
                            elif xpoint == 0:
                                xpoint = xpoint + 20
                            if ypoint == y:
                                ypoint = ypoint - 20
                            elif ypoint == 0:
                                ypoint = ypoint + 20

                            moveMouseAbs(xpoint, ypoint)
                            command_buffer = ["网格"]
                        else:
                            return self.handle_invalid_command(
                                command_buffer[2], command_buffer
                            )
                else:
                    return self.handle_invalid_command(
                        command_buffer[1], command_buffer
                    )
        else:
            command_buffer = []

        return command_buffer
