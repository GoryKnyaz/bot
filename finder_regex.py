import re
from typing import List


class Finder:
    def __init__(self, reg_ex_string=''):
        self.reg_ex = reg_ex_string

    def findIn(self, text: str):
        re.search(self.reg_ex, text)

    def findInMass(self, massText: List[str]):
        for text in massText:
            re.search(self.reg_ex, text)
