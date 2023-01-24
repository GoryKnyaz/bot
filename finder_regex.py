import re
from typing import List


class Finder:
    def __init__(self, reg_ex_string='', marker=''):
        self.reg_ex = reg_ex_string
        self.marker = marker

    def findIn(self, text: str):
        re.findall(self.reg_ex, text)

    def findInMass(self, massText: List[str]):
        for text in massText:
            re.findall(self.reg_ex, text)
