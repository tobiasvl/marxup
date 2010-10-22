import re

class Tiki:
    groups = ['text', 'meta']

    def __init__(raw, context = None):
        self.raw = raw
        self.context = context

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
