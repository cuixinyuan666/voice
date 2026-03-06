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
from .mouse_parser import MouseParser
from .text_parser import TextParser
from .command_parser import CommandParser
from .alpha_parser import AlphaParser


class Parser:
    def __init__(self):
        self.state = "命令"
        self.command_buffer = []
        self.pause = False

        self.stepmapping = {
            "一": 10,
            "二": 30,
            "三": 50,
            "四": 100,
            "五": 300,
            "六": 500,
            "七": 1000,
            "八": 1500,
        }

        self.states = ["文本", "命令", "鼠标", "暂停", "字母"]
        self.steps = ["一", "二", "三", "四", "五", "六", "七", "八"]

        self.mouseParser = MouseParser(self.stepmapping)
        self.textParser = TextParser(self.stepmapping)
        self.commandParser = CommandParser(self.stepmapping)
        self.alphaParser = AlphaParser()

        # nontextcommands can be fed to a speech to text model to make it work more effectively for commands
        self.nontextcommands = list(
            set(self.states)
            | set(self.steps)
            | set(self.commandParser.commandlist)
            | set(self.mouseParser.commands)
        )
        self.alphavalues = (
            self.alphaParser.keywords
            + self.states
            + self.commandParser.stateless_commands
        )

    # ingest string that may contain multiple space delimited words, where each word is a sent to parser individually
    def ingest(self, words):
        # print(word.lower())
        for word in words.split(" "):
            if word != "":
                self.command_buffer.append(word.lower())

        if len(self.command_buffer) > 0:

            if not self.pause:
                print(
                    self.command_buffer
                )  # makes it easy to see current state of command_buffer

            self.evaluate()

    def evaluate(self):

        if self.pause:

            if self.command_buffer[0] == "开始":
                if len(self.command_buffer) >= 2:
                    if self.command_buffer[1] == "工作":
                        self.state = "命令"
                        self.pause = False
                        self.command_buffer = []
                        print("Sidekick 重新开始工作")
            else:
                self.command_buffer = []

        else:
            # either set state or parse command
            if self.command_buffer[-1] == "暂停":
                self.pause = True
                self.state = "文本"  # this ensures 'pause' is not accidentally triggered by model with smaller search space
                print("Sidekick 正在休息")
                self.command_buffer = []
            elif self.command_buffer[-1] == "命令":
                self.state = "命令"
                self.command_buffer = []
            elif self.command_buffer[-1] == "文本":
                self.state = "文本"
                self.command_buffer = []
            elif self.command_buffer[-1] == "字母":
                self.state = "字母"
                self.command_buffer = []
            elif self.command_buffer[-1] == "鼠标":
                self.state = "鼠标"
                self.command_buffer = []
                self.command_buffer, self.state = self.mouseParser.evaluate_mouse(
                    self.command_buffer
                )
            else:  # send command to appropriate parsing function
                if len(self.command_buffer) > 0:
                    (
                        stateless,
                        self.command_buffer,
                    ) = self.commandParser.stateless_command(self.command_buffer)
                    if not stateless:
                        if self.state == "命令":
                            self.command_buffer = self.commandParser.evaluate_command(
                                self.command_buffer
                            )
                        elif self.state == "文本":
                            self.command_buffer = self.textParser.evaluate_text(
                                self.command_buffer
                            )
                        elif self.state == "字母":
                            self.command_buffer = self.alphaParser.evaluate_text(
                                self.command_buffer
                            )
                        elif self.state == "鼠标":
                            (
                                self.command_buffer,
                                self.state,
                            ) = self.mouseParser.evaluate_mouse(self.command_buffer)
            
        # stop mouse if state is switched before stopping
        if not self.mouseParser.stopMouse and self.state != "鼠标":
            self.mouseParser.stopMouse = True
