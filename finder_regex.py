import re

from typing import List


class Finder:
    """
    This is a class that specializes in storing a regular expression and using it to match a pattern in text.
    """

    def __init__(self, reg_ex_string=r'', marker=''):
        """
        Constructor
        :param reg_ex_string: the regular expression itself.
        :type reg_ex_string: str
        :param marker: regex type indicating what the regex is for.
        :type marker: str
        """
        self.reg_ex = reg_ex_string
        self.marker = marker

    def findIn(self, text: str):
        """
        A function to find all matches for a given regular expression.
        :param text: string to apply regular expression.
        :type text: str

        :rtype: List[str]
        :return: array of matches.
        """
        return re.findall(self.reg_ex, text)

    def findInMass(self, massText: List[str]):
        """
         A function to find all matches for a given regular expression.
        :param massText: array of strings to apply to each regular expression.
        :type massText: List(str)

        :rtype: List[str]
        :return: array of matches for each string of the array of strings.
        """
        result = []
        for text in massText:
            result.append(re.findall(self.reg_ex, text))
        return result
