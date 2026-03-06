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


class AlphaParser:
    def __init__(self):
        self.numbers = [
            "零",
            "一",
            "二",
            "三",
            "四",
            "五",
            "六",
            "七",
            "八",
            "九",
        ]
        self.punctuation = [
            "右括号",
            "左括号",
            "右方括号",
            "等于",
            "左方括号",
            "句号",
            "冒号",
            "破折号",
            "逗号",
            "下划线",
            "问号",
            "点",
            "井号",
            "分号",
            "感叹号",
            "大写",
            "感叹号",
            "引号",
            "单引号",
        ]
        self.keywords = list(string.ascii_lowercase) + self.punctuation + self.numbers

    def word_to_int(self, word):
        mapping = {
            "零": "0",
            "一": "1",
            "二": "2",
            "三": "3",
            "四": "4",
            "五": "5",
            "六": "6",
            "七": "7",
            "八": "8",
            "九": "9",
        }
        return mapping[word]

    def insert_punctuation(self, text):
        if text == "句号" or text == "点":
            text = text.replace("句号", ".").replace("点", ".")
        elif text == "等于":
            text = text.replace("等于", "=")
        elif text == "右括号":
            text = text.replace("右括号", ")")
        elif text == "左括号":
            text = text.replace("左括号", "(")
        elif text == "左方括号":
            text = text.replace("左方括号", "[")
        elif text == "右方括号":
            text = text.replace("右方括号", "]")
        elif text == "冒号":
            text = text.replace("冒号", ":")
        elif text == "破折号":
            text = text.replace("破折号", "-")
        elif text == "逗号":
            text = text.replace("逗号", ",")
        elif text == "问号":
            text = text.replace("问号", "?")
        elif text == "引号":
            text = text.replace("引号", '"')
        elif text == "井号":
            text = text.replace("井号", "#")
        elif text == "单引号":
            text = text.replace("单引号", "'")
        elif text == "下划线":
            text = text.replace("下划线", "_")
        elif text == "分号":
            text = text.replace("分号", ";")
        elif text == "感叹号":
            text = text.replace("感叹号", "!")

        return text

    def evaluate_text(self, command_buffer):
        if command_buffer[0] == "大写":  # capitalize next word spoken
            if len(command_buffer) >= 2:
                writeToScreen(command_buffer[1].capitalize())
                if len(command_buffer) > 2:
                    command_buffer = command_buffer[2:]
                else:
                    command_buffer = []
        else:
            for i in range(0, len(command_buffer)):
                # some punctuation includes backspace and space after - other does not
                if command_buffer[i] in self.punctuation:
                    writeToScreen(self.insert_punctuation(command_buffer[i]))
                elif command_buffer[i] in self.numbers:
                    writeToScreen(self.word_to_int(command_buffer[i]))
                else:
                    writeToScreen(command_buffer[i])

            command_buffer = []

        return command_buffer
