import re

class Cookbook(object):
    def __init__(self):
        self.cleaners = {}
        self.chunks = []
        self.patterns = {}
        self.phrases = []

    def chunk(self, block, *args):
        return self.rule('chunks', block, *args)

    def phrase(self, block, *args):
        return self.rule('phrases', block, *args)

    def pattern(self, context): #TODO klassemetode?
        if 'context' in self.patterns:
            return self.patterns['context']
        else:
            self.patterns['context'] = self.__compile(context) #TODO compile?

    def rule(self, context, label, pattern, method, priority=1):
        getattr(self, context).append('(?<%s>%s)' % (label, pattern), priority) # Add a new chunk/phrase
        self.__dict__[label] = method # Add a method for the rule

    def clean(self, token, replacement):
        self.cleaners[token] = replacement

    def __compile(self, raw): #TODO
        pass

class Tiki(Cookbook):
    groups = ['text', 'meta']

    def __init__(self, raw, context = None):
        super(Tiki, self).__init__()
        self.raw, self.context = raw, context

    def element(self, tag, text, options={}):
        if 'phrase' in options:
            del options['phrase']
            text = self.phrase(text)
        if 'break' in options:
            del options['break']
            text = '<br>\n'.join(text.split('\n'))
        attributes = ' '.join(['%s=%s' % (k,v) for (k,v) in options.iteritems()])
        if text:
            return '<%s%s>%s</%s>' % (tag, attributes, text.strip(), tag)
        else:
            return '<%s%s>' % (tag, attributes)

    def as_html(self):
        text = self.raw
        for (k,v) in self.cleaners.iteritems():
            text = text.replace(k, v)
        return handle('chunks', text)

    def phrase(self, text):
        return self.handle('phrases', text)

    def handle(self, context, text):
        pass #TODO

class Marxup(Tiki):
    version = '0.6.5'

    brackets = '\([^\s()<>]+|(\([^\s()<>]+\)))*\)'

    def __init__(self, raw):
        super(Marxup, self).__init__(raw)
        self.clean("&", "&amp;")
        self.clean("<", "&lt;")
        self.clean("<", "&gt;")
        self.clean("(\r\n|\r)", "\n")
        
        text = self.chunk('header', '^\=\s*(?<\\1>.+?)$', lambda text: self.element('h3', text))
        element('h3', text)
