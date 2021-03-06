#vim: set fileencoding=utf-8
import re, inspect

class Cookbook(object):
    def __init__(self):
        self.cleaners = {}
        self.precleaners = {}
        self.chunks = []
        self.patterns = {}
        self.phrases = []

    def chunk(self, element, *args):
        return self.rule(element, 'chunks', *args)

    def phrase(self, element, *args):
        return self.rule(element, 'phrases', *args)

    def pattern(self, context): 
        """Create a regexp (and cache it)"""
        if context not in self.patterns:
            self.patterns[context] = self.__compile(getattr(self, context))
        return self.patterns[context]

    def rule(self, element, context, label, pattern, priority=1):
        getattr(self, context).append(('(?P<%s>%s)' % (label, pattern), priority)) # Add a new chunk/phrase
        self.__dict__[label] = element # Add a method for the rule

    def preclean(self, token, replacement):
        self.precleaners[token] = replacement

    def clean(self, token, replacement):
        self.cleaners[token] = replacement

    def __compile(self, raw):
        """Builds a regexp with all patterns, sorted by priority"""
        elements = [rule[0] for rule in sorted(raw, key=lambda (pattern, priority): priority)] # Sort by priority
        a = '|'.join(elements) # Build a regexp union
        return re.compile(a, re.MULTILINE) # Build a regexp union

class Tiki(Cookbook):
    groups = ['text', 'meta'] # The different match groups we want to treat differently

    def __init__(self, raw, context = None):
        super(Tiki, self).__init__()
        self.raw, self.context = raw, context

    def element(self, tag, text, options={}):
        if 'phrase' in options:
            del options['phrase']
            text = self.phrase2(text)
        if 'break' in options:
            del options['break']
            text = '<br>\n'.join(text.split('\n')) # Break at newline
        attributes = ' '.join([' %s="%s"' % (k,v) for (k,v) in options.iteritems()])
        if text:
            return '<%s%s>%s</%s>' % (tag, attributes, text.strip(), tag)
        else:
            return '<%s%s>' % (tag, attributes)

    def as_html(self):
        """Convert the Marxup to HTML."""
        text = self.raw
        # Initial cleaning/escaping
        for (k, v) in self.precleaners.iteritems():
            text = text.replace(k, v)
        for (k, v) in self.cleaners.iteritems():
            text = text.replace(k, v)
        return self.handle('chunks', text)

    def phrase2(self, text):
        return self.handle('phrases', text)

    def handle(self, context, text):
        def repl(match):
            method = getattr(self, match.lastgroup)
            method_arity = len(inspect.getargspec(method)[0])
            args = map(lambda arg: match.group(arg), [a + '_' + match.lastgroup for a in Tiki.groups[:method_arity]])
            return getattr(self, match.lastgroup)(*args)
        pattern = self.pattern(context)
        # TODO when porting this code to python 2.7 (when Cheetah is okay
        # with it), change this to be compliant?
        return re.sub(pattern, repl, text)

class Marxup(Tiki):
    version = '1x'       # Version of Marxup (syntax/semantics)
    implementation = 'a' # Version of implementation (behind the scenes)

    brackets = '\([^\s()<>]+|(\([^\s()<>]+\)))*\)'

    def __init__(self, raw):
        super(Marxup, self).__init__(raw)
        # Clean up the input and make it fit for HTML:
        self.preclean("&", "&amp;")   # Safe for HTML entities
        self.clean("<", "&lt;")       # Safe for HTML elements
        self.clean(">", "&gt;")
        self.clean("(\r\n|\r)", "\n") # Fix Windows newlines

        # Define chunks:
        self.chunk(lambda text: self.element('h3', text), 'header', '^\=\s*(?P<text_header>.+?)$')
        self.chunk(lambda text: self.element('p', text, {'phrase': True, 'break': True}), 'paragraph', '((?m)^(?P<text_paragraph>\S.*?)(?:\n\n|\Z|\n\Z))', 5)
        self.chunk(lambda text: self.element('span', text, {'class': 'important'}), 'important', '!!!\s*(?P<text_important>.+?)\s*!!!', 2)
        
        def code(text, meta):
            code = self.element('code', text, {'class': meta})
            if not code:
                code = 'unknown'
            return code
        self.chunk(lambda text, meta: self.element('pre', code(text, meta)), 'code', '((?m)^\{\{\{(\s*&lt;(?P<meta_code>.+?)&gt;)?(?P<text_code>.+?)\}\}\})')

        def list(text):
            """Parse a Marxup list and create a HTML list"""
            html, stack = '', []
            list = re.finditer('((?xm)^\s* ([#\*]+) \s* (.+?) $)', text)
            for match in list:
                level = match.group(2) # Level of indentation
                text = match.group(3)  # List element text
                if level[0] == '#':
                    # Ordered list
                    type = 'ol'
                else:
                    # Unordered list
                    type = 'ul'
                item = self.element('li', text, {'phrase': True})
                if len(level) > len(stack):
                    html += '<%s>' % type
                    stack.append('</%s>' % type)
                if len(level) < len(stack):
                    try:
                        html += stack.pop() # Popping an empty stack causes IndexError
                    except: 
                        pass
                html += item
            if stack:
                for i in reversed(stack):
                    html += i
            return html
        self.chunk(list, 'list', '^(?P<text_list>([#\*]+\s.+?$\n?)+(\Z|(?!^\s*[#\*])))', 3)

        # Define phrases:
        self.phrase(lambda text: self.element('b', text, {'phrase': True}), 'bold', '(?<![\~])\*(?P<text_bold>.+?)\*')
        self.phrase(lambda text: self.element('i', text, {'phrase': True}), 'italic', '(?<![\~\:<])_(?P<text_italic>.+?)_')
        self.phrase(lambda text: self.element('tt', text), 'tt', '(?<![\~])´(?P<text_tt>.+?)´')
        self.phrase(lambda text, meta: self.element('a', text, {'href': meta, 'rel': 'nofollow'}), 'link', '\+(?P<text_link>[\w\*\'\:\!\,\.\-·\? ]+?)\+(\s*\((?P<meta_link>(http|gopher|ftp):\/\/.+?)\))', 0) #TODO more robust URL regex
        self.phrase(lambda text: self.element('span', '&hearts;', {'class': 'heart'}), 'heart', '(?P<text_heart>&lt;3)', 2)
        self.phrase(lambda text, meta: self.element('img', None, {'src': text, 'alt': '', 'title': meta}), 'image', '\&lt;(?P<text_image>\S+)\&gt;(\s*\((?P<meta_image>.+)\))?')
