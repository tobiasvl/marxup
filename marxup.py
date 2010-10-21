import re

class Tiki:
    cleaners = {}
    pre_cleaners = {}
    patterns = {}
    chunk = []
    phrase = []

    def __init__(chunk, phrase):
        self.chunk = chunk
        self.phrase = phrase

    def as_html():
        pass

    def handle(context, text):
        pass

    def element(tag, text, phrased):
        pass

    def inline_element(tag, text, phrased):
        pass

    def pattern(context):
        pass

    def rule(context, label, pattern, priority):
        pass

    def clean(token, replacement):
        pass

    def pre_clean(token, replacement):
        pass

class Marxup(Tiki):
    def __init__():
        pre_clean("&", "&amp;")
        clean("<", "&lt;")
        clean("<", "&gt;")

        #rules go here
