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
        a = '|'.join(elements) # Build a regexp union
        print a
        return re.compile(a, re.MULTILINE) # Build a regexp union

class Tiki(Cookbook):
    groups = ['text', 'meta']

    def __init__(self, raw, context = None):
        super(Tiki, self).__init__()
        self.raw, self.context = raw, context

    def element(self, tag, text, options={}):
        if 'phrase' in options:
            del options['phrase']
            text = self.phrase2(text)
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

    def phrase2(self, text):
        return self.handle('phrases', text)

    def handle(self, context, text):
        def repl(match):
            print match.groupdict()
            print match.lastgroup
            method = getattr(self, match.lastgroup)
            method_arity = len(inspect.getargspec(method)[0])
            args = map(lambda arg: match.group(arg), [a + '_' + match.lastgroup for a in Tiki.groups[:method_arity]])
            return getattr(self, match.lastgroup)(*args)
        pattern = self.pattern(context)
        # TODO when porting this code to python 2.7 (when Cheetah is okay
        # with it), change this to be compliant?
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

        # Define chunks:
        self.chunk(lambda text: self.element('h3', text), 'header', '^\=\s*(?P<text_header>.+?)$')
        self.chunk(lambda text: self.element('p', text), 'paragraph', '((?m)^(?P<text_paragraph>\S.+?)(?:\\n\\n|\z))', 5)
        self.chunk(lambda text: self.element('pre', text), 'code', '((?m)^\{\{\{(\s*&lt;(?P<meta>.+?)&gt;)?(?P<text_code>.+?)\}\}\})')

        # Define phrases:
        self.phrase(lambda text: self.element('span', text), 'heart', '&hearts;', 2)
        self.phrase(lambda text: self.element('i', text), 'italic', '(?<![\~\:<])_(?P<text_italic>.+?[^\~\:<])_')
