import re

class Tiki:
    groups = ['text', 'meta']

    def __init__(raw, context = None):
        self.raw = raw
        self.context = context

    def element(tag, text, options={}):
        if 'phrase' in options:
            del options['phrase']
            text = phrase(text)
        if 'break' in options:
            del options['break']
            text = '<br>\n'.join(text.split('\n'))
        attributes = ' '.join(['%s=%s' % (k,v) for (k,v) in options.iteritems()])
        if text:
            return '<%s%s>%s</%s>' % (tag, attributes, text.strip(), tag)
        else:
            return '<%s%s>' % (tag, attributes)

    def as_html():
        pass

    def phrase(text):
        return handle('phrases', text)

    def handle(context, text):
        pass

class Cookbook
    cleaners = {}
    chunks = []
    patterns = {}
    phrases = []

    def pattern(context):
        if 'context' in self.patterns:
            return self.patterns['context']
        else:
            self.patterns['context'] = self.compile(context)

    def rule(context, label, pattern, priority=1, method):
        pass

    def clean(token, replacement):
        self.cleaners[token] = replacement

class Marxup(Tiki):
    version = '0.6.5'

    brackets = '\([^\s()<>]+|(\([^\s()<>]+\)))*\)'

    def __init__():
        pre_clean("&", "&amp;")
        clean("<", "&lt;")
        clean("<", "&gt;")

        #rules go here
