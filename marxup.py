import re, inspect

class Cookbook(object):
    def __init__(self):
        self.cleaners = {}
        self.chunks = []
        self.patterns = {}
        self.phrases = []

    def chunk(self, element, *args):
        return self.rule(element, 'chunks', *args)

    def phrase(self, element, *args):
        return self.rule(element, 'phrases', *args)

    def pattern(self, context): #TODO klassemetode?
        """Create a regexp (and cache it)"""
        if context not in self.patterns:
            self.patterns[context] = self.__compile(getattr(self, context))
        return self.patterns[context]

    def rule(self, element, context, label, pattern, priority=1):
        getattr(self, context).append(('(?P<%s>%s)' % (label, pattern), priority)) # Add a new chunk/phrase
        self.__dict__[label] = element # Add a method for the rule

    def clean(self, token, replacement):
        self.cleaners[token] = replacement

    def __compile(self, raw):
        """Builds a regexp with all patterns, sorted by priority"""
        elements = [rule[0] for rule in sorted(raw, key=lambda (pattern, priority): priority)] # Sort by priority
        return '|'.join(elements) # Build a regexp union

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
        for (k, v) in self.cleaners.iteritems():
            text = text.replace(k, v)
        return self.handle('chunks', text)

    def phrase(self, text):
        return self.handle('phrases', text)

    def handle(self, context, text):
        def repl(match):
            method = getattr(self, match.lastgroup)
            method_arity = len(inspect.getargspec(method)[0])
            args = map(lambda arg: match.group(arg), Tiki.groups[:method_arity])
            print match
            print method
            print args
            return getattr(self, match.lastgroup)(*args)

        pattern = self.pattern(context)
        print pattern
        return re.sub(pattern, repl, text)

class Marxup(Tiki):
    version = '0.6.5'

    brackets = '\([^\s()<>]+|(\([^\s()<>]+\)))*\)'

    def __init__(self, raw):
        super(Marxup, self).__init__(raw)
        self.clean("&", "&amp;")
        self.clean("<", "&lt;")
        self.clean("<", "&gt;")
        self.clean("(\r\n|\r)", "\n")

        self.chunk(lambda text: self.element('h3', text), 'header', '^\=\s*(?P<text>.+?)$')
    #    self.phrase(lambda text: self.element('span', text), 'heart', '&lt;3')
