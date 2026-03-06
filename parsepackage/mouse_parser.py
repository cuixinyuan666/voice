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
import threading
import math


class MouseParser:
    def __init__(self, steps):
        self.mouseStarted = False
        self.steps = steps
        self.stopMouse = True

        self.commands = [
            "停止",
            "极慢",
            "慢速",
            "快速",
            "中速",
            "向上",
            "向下",
            "逆时针",
            "顺时针",
            "北",
            "南",
            "东",
            "西",
            "一",
            "二",
            "三",
            "四",
            "东北",
            "西北",
            "东南",
            "西南",
        ]

    def evaluate_mouse(self, command_buffer):
        if not self.mouseStarted:
            self.stopMouse = False
            self.magnitude = 5  # in pixels
            self.sleep = 0.2
            self.setMouseCoord(90)

        if len(command_buffer) > 0:
            if "停止" in command_buffer[0]:
                self.stopMouse = True
                command_buffer = []
                return [command_buffer, "command"]
            elif "极慢" in command_buffer[0]:
                self.magnitude = 5
                self.sleep = 0.2
                self.setMouseCoord(self.currentangle)
            elif "慢速" in command_buffer[0]:
                self.magnitude = 15
                self.sleep = 0.2
                self.setMouseCoord(self.currentangle)
            elif "快速" in command_buffer[0]:
                self.magnitude = 50
                self.sleep = 0.5
                self.setMouseCoord(self.currentangle)
            elif "中速" in command_buffer[0]:
                self.magnitude = 25
                self.sleep = 0.3
                self.setMouseCoord(self.currentangle)
            elif "向上" in command_buffer[0] or "逆时针" in command_buffer[0]:
                self.setMouseCoord(self.currentangle + 15)
            elif "向下" in command_buffer[0] or "顺时针" in command_buffer[0]:
                self.setMouseCoord(self.currentangle - 15)
            elif "北" in command_buffer[0]:
                self.setMouseCoord(90)
            elif "南" in command_buffer[0]:
                self.setMouseCoord(270)
            elif "东" in command_buffer[0]:
                self.setMouseCoord(0)
            elif "西" in command_buffer[0]:
                self.setMouseCoord(180)
            elif "东北" in command_buffer[0] or "一" in command_buffer[0]:
                self.setMouseCoord(35)
            elif (
                "西北" in command_buffer[0]
                or "二" in command_buffer[0]
            ):
                self.setMouseCoord(135)
            elif "西南" in command_buffer[0] or "三" in command_buffer[0]:
                self.setMouseCoord(225)
            elif (
                "东南" in command_buffer[0]
                or "四" in command_buffer[0]
            ):
                self.setMouseCoord(315)

            command_buffer = []

            if not self.mouseStarted:
                self.startMouse()

        return [command_buffer, "mouse"]

    def startMouse(self):
        thread = threading.Thread(target=self.mouse_thread)
        thread.daemon = True
        thread.start()
        self.mouseStarted = True

    def setMouseCoord(self, degrees):
        self.currentangle = degrees
        self.x = self.magnitude * math.cos(math.radians(degrees))
        self.y = -1 * self.magnitude * math.sin(math.radians(degrees))

    def mouse_thread(self):
        while True:
            if self.stopMouse:
                self.mouseStarted = False
                break
            else:
                moveMouse(self.x, self.y)
                time.sleep(self.sleep)
