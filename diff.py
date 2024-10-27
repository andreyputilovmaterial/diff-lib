

from collections import namedtuple

# DiffItemKeep = namedtuple('DiffItemKeep', ['line'])
# DiffItemInsert = namedtuple('DiffItemInsert', ['line'])
# DiffItemRemove = namedtuple('DiffItemRemove', ['line'])

class DiffItemKeep(namedtuple('DiffItemKeep',['line'])):
    __slots__ = ()
    def __str__(self):
        return 'keep: {line}'.format(line=self.line)
class DiffItemInsert(namedtuple('DiffItemInsert',['line'])):
    __slots__ = ()
    def __str__(self):
        return 'insert: {line}'.format(line=self.line)
class DiffItemRemove(namedtuple('DiffItemRemove',['line'])):
    __slots__ = ()
    def __str__(self):
        return 'remove: {line}'.format(line=self.line)


def unicode_remove_accents(txt):
    raise Exception('remove accents func: not implemented; please grab some implementation suitable for your needs')





# a function or Myers diff
# re-written to python from js by AP 11/30/2022
# sourced 11/17/2022 from https://github.com/wickedest/myers-diff, Apache 2.0 license */ /* authors can be found there on that page */ /* license is not attached but can be found here https:/* github.com/wickedest/myers-diff/blob/master/LICENSE */

class MyersDiffSplitter:
    def __init__(self,data,delimiter):
        self.data = data
        self.pos = None
        self.start = None
        self.delimiter = delimiter
    def __iter__(self):
        self.start = 0
        self.pos = ( 0 if not self.delimiter else ( data.index(self.delimiter, self.start) if self.delimiter in self.data[self.start:] else -1 ) )
        return self
    def __next__(self):
        if len(self.data) == 0:
            raise StopIteration
        elif not self.delimiter:
            if self.start>=len(self.data):
                raise StopIteration
            else:
                part = {'text':self.data[self.start],'pos':self.start}
                self.start = self.start + 1
                return part
        elif self.pos<0:
            if self.start<=len(self.data):
                # handle remaining text.  the `start` might be at some */ /*  position less than `text.length`.  it may also be _exactly_ */ /*  `text.length` if the `text` ends with a double `ch`, e.g. */ /*  "\n\n", the `start` is set to `pos + 1` below, which is one */ /*  after the first "\n" of the pair.  it would also be split. */
                part = {'text':self.data[self.start:],'pos':self.start}
                self.pos = -1
                self.start = len(self.data) + 1
                return part
            else:
                raise StopIteration
        else:
            word = self.data[self.start:self.pos]
            part = {'text':word,'pos':self.start}
            self.start = self.pos + 1
            self.pos = ( 0 if not self.delimiter else ( data.index(self.delimiter, self.start) if self.delimiter in self.data[self.start:] else -1 ) )
            return part

def myers_diff_get_default_settings():
    return {
        'compare': 'array', # array|lines|words|chars
        'ignorewhitespace': False,
        'ignorecase': False,
        'ignoreaccents': False
    }

class MyersDiffEncodeContext:
    def __init__(self, encoder, data, options={}):
        re = None
        self.encoder = encoder
        self._codes = {}
        self._modified = {}
        self._parts = [];
        count = 0
        splitter_delimiter = None
        if 'compare' in options:
            if options['compare']=='lines':
                splitter_delimiter = "\n"
            elif options['compare']=='words':
                splitter_delimiter = ' '
            elif options['compare']=='chars':
                splitter_delimiter = ''
            elif options['compare']=='array':
                splitter_delimiter = None
            else:
                # default
                # that would be chars, or array, that would work the same
                splitter_delimiter = None
        split = MyersDiffSplitter(data,splitter_delimiter)
        part = None
        for part in split:
            # if options.lowercase..., options.ignoreAccents
            # line = lower(line) ...
            # part = { 'text': part_txt, 'pos': count }
            line = str(part['text'])
            if ('ignorewhitespace' in options) and (options['ignorewhitespace']):
                line = re.sub(r'^\s*','',re.sub(r'\s*$','',re.sub(r'\s+',' ',line)))
            if ('ignorecase' in options) and (options['ignorecase']):
                line = line.lower()
            if ('ignoreaccents' in options) and (options['ignoreaccents']):
                line = unicode_remove_accents(line)
            aCode = encoder.get_code(line)
            self._codes[str(count)] = aCode
            self._parts.append(part)
            count = count + 1
    def finish(self):
        del self.encoder
    def _get_codes(self):
        return self._codes
    def _get_length(self):
        return len(self._codes.keys())
    def _get_modified(self):
        return self._modified
    codes = property(_get_codes)
    modified = property(_get_modified)
    length = property(_get_length)

class MyersDiffEncoder:
    code = 0
    diff_codes = {}
    def __init__(self):
        self.code = 0
        self.diff_codes = {}
    def encode(self, data,options={}):
        return MyersDiffEncodeContext(self,data,options)
    def get_code(self, line):
        if str(line) in self.diff_codes:
            return self.diff_codes[str(line)]
        self.code = self.code + 1
        self.diff_codes[str(line)] = self.code
        return self.code

class Myers:
    @staticmethod
    def compare_lcs(lhsctx, rhsctx, callback):
        lhs_start = 0
        rhs_start = 0
        lhs_line = 0
        rhs_line = 0
        while ((lhs_line < lhsctx.length) or (rhs_line < rhsctx.length)):
            if not str(lhs_line) in lhsctx.modified:
                lhsctx.modified[str(lhs_line)] = False
            if not str(rhs_line) in rhsctx.modified:
                rhsctx.modified[str(rhs_line)] = False
            if ((lhs_line < lhsctx.length) and (not lhsctx.modified[str(lhs_line)]) and (rhs_line < rhsctx.length) and (not rhsctx.modified[str(rhs_line)])):
                # equal lines
                lhs_line = lhs_line + 1
                rhs_line = rhs_line + 1
            else:
                # maybe deleted and/or inserted lines
                lhs_start = lhs_line
                rhs_start = rhs_line
                while ((lhs_line < lhsctx.length) and ((rhs_line >= rhsctx.length) or ((str(lhs_line) in lhsctx.modified) and (lhsctx.modified[str(lhs_line)])))):
                    lhs_line = lhs_line + 1
                while ((rhs_line < rhsctx.length) and ((lhs_line >= lhsctx.length) or ((str(rhs_line) in rhsctx.modified) and (rhsctx.modified[str(rhs_line)])))):
                    rhs_line = rhs_line + 1
                if ((lhs_start < lhs_line) or (rhs_start < rhs_line)):
                    lat = min([lhs_start, lhsctx.length-1 if lhsctx.length>0 else 0])
                    rat = min([rhs_start, rhsctx.length-1 if rhsctx.length>0 else 0])
                    lpart = lhsctx._parts[min([lhs_start, lhsctx.length - 1])]
                    rpart = rhsctx._parts[min([rhs_start, rhsctx.length - 1])]
                    item = {
                        'lhs': {
                            'at': lat,
                            'del': lhs_line - lhs_start,
                            'pos': lpart['pos'] if lpart else None,
                            'text': lpart['text'] if lpart else None
                        },
                        'rhs': {
                            'at': rat,
                            'add': rhs_line - rhs_start,
                            'pos': rpart['pos'] if rpart else None,
                            'text': rpart['text'] if rpart else None
                        }
                    }
                    callback(item)

    @staticmethod
    def get_shortest_middle_snake(lhsctx, lhs_lower, lhs_upper, rhsctx, rhs_lower, rhs_upper, vectorU, vectorD):
        max = lhsctx.length + rhsctx.length + 1
        if not max:
            raise Exception('unexpected state');
        kdown = lhs_lower - rhs_lower
        kup = lhs_upper - rhs_upper
        delta = (lhs_upper - lhs_lower) - (rhs_upper - rhs_lower)
        odd = (delta & 1) != 0
        offset_down = max - kdown
        offset_up = max - kup
        maxd = ((lhs_upper - lhs_lower + rhs_upper - rhs_lower) // 2) + 1
        ret = {
            'x': 0,
            'y': 0
        }
        d = None
        k = None
        x = None
        y = None
        if offset_down + kdown + 1>=len(vectorD):
            # redim
            # print('redim {var} to {n}, len is {l}!'.format(var='vectorD',n=offset_down + kdown + 1,l=len(vectorD)))
            raise Exception('redim {var} to {n}, len is {l}!'.format(var='vectorD',n=offset_down + kdown + 1,l=len(vectorD)))
            # vectorD = [*vectorD,*[None for i in range(len(vectorD),offset_down + kdown + 1+1)]]
        vectorD[offset_down + kdown + 1] = lhs_lower
        if offset_up + kup - 1>=len(vectorU):
            # redim
            # print('redim {var} to {n}, len is {l}!'.format(var='vectorU',n=offset_up + kup - 1,l=len(vectorU)))
            raise Exception('redim {var} to {n}, len is {l}!'.format(var='vectorU',n=offset_up + kup - 1,l=len(vectorU)))
            # vectorU = [*vectorU,*[None for i in range(len(vectorU),offset_up + kup - 1+1)]]
        vectorU[offset_up + kup - 1] = lhs_upper
        for d in range(maxd+1):
            for k in range(kdown - d, kdown + d+1, 2):
                if (k == kdown - d):
                    x = vectorD[offset_down + k + 1]
                    # down
                else:
                    x = vectorD[offset_down + k - 1] + 1
                    # right
                    if ((k < (kdown + d)) and (vectorD[offset_down + k + 1] >= x)):
                        x = vectorD[offset_down + k + 1]
                        # down
                y = x - k
                # find the end of the furthest reaching forward D-path in diagonal k.
                while ((x < lhs_upper) and (y < rhs_upper) and (lhsctx.codes[str(x)] == rhsctx.codes[str(y)])):
                    x = x + 1
                    y = y + 1
                if offset_down + k>=len(vectorD):
                    # redim
                    # print('redim {var} to {n}, len is {l}!'.format(var='vectorD',n= offset_down + k,l=len(vectorD)))
                    raise Exception('redim {var} to {n}, len is {l}!'.format(var='vectorD',n= offset_down + k,l=len(vectorD)))
                    # vectorD = [*vectorD,*[None for i in range(len(vectorD),offset_down + k+1)]]
                vectorD[offset_down + k] = x
                # overlap ?
                if (odd and (kup - d < k) and (k < kup + d)):
                    if (vectorU[offset_up + k] <= vectorD[offset_down + k]):
                        ret['x'] = vectorD[offset_down + k]
                        ret['y'] = vectorD[offset_down + k] - k
                        return (ret)
            # Extend the reverse path.
            for k in range(kup - d, kup + d+1, 2):
                # find the only or better starting point
                if (k == kup + d):
                    x = vectorU[offset_up + k - 1]
                    # up
                else:
                    x = vectorU[offset_up + k + 1] - 1
                    # left
                    if ((k > kup - d) and (vectorU[offset_up + k - 1] < x)):
                        x = vectorU[offset_up + k - 1]
                        # up
                y = x - k
                while ((x > lhs_lower) and (y > rhs_lower) and (lhsctx.codes[str(x - 1)] == rhsctx.codes[str(y - 1)])):
                    # diagonal
                    x = x - 1
                    y = y - 1
                if offset_up + k>=len(vectorU):
                    # redim
                    # print('redim {var} to {n}, len is {l}!'.format(var='vectorU',n= offset_up + k,l=len(vectorU)))
                    raise Exception('redim {var} to {n}, len is {l}!'.format(var='vectorU',n= offset_up + k,l=len(vectorU)))
                    # vectorU = [*vectorU,*[None for i in range(len(vectorU),offset_up + k+1)]]
                vectorU[offset_up + k] = x
                # overlap ?
                if (not odd and (kdown - d <= k) and (k <= kdown + d)):
                    if offset_up + k>=len(vectorU):
                        # redim
                        # print('redim {var} to {n}, len is {l}!'.format(var='vectorU',n=offset_up + k,l=len(vectorU)))
                        raise Exception('redim {var} to {n}, len is {l}!'.format(var='vectorU',n=offset_up + k,l=len(vectorU)))
                        # vectorU = [*vectorU,*[None for i in range(len(vectorU),offset_up + k+1)]]
                    if offset_down + k>=len(vectorD):
                        # redim
                        # print('redim {var} to {n}, len is {l}!'.format(var='vectorD',n=offset_down + k,l=len(vectorD)))
                        raise Exception('redim {var} to {n}, len is {l}!'.format(var='vectorD',n=offset_down + k,l=len(vectorD)))
                        # vectorD = [*vectorD,*[None for i in range(len(vectorD),offset_down + k+1)]]
                    if (vectorU[offset_up + k] <= vectorD[offset_down + k]):
                        ret['x'] = vectorD[offset_down + k]
                        ret['y'] = vectorD[offset_down + k] - k
                        return (ret)
        # should never get to this state
        raise Exception('unexpected state')
    @staticmethod
    def get_longest_common_subsequence(lhsctx, lhs_lower, lhs_upper, rhsctx, rhs_lower, rhs_upper, vectorU, vectorD):
        # trim off the matching items at the beginning
        while ((lhs_lower < lhs_upper) and (rhs_lower < rhs_upper) and (lhsctx.codes[str(lhs_lower)] == rhsctx.codes[str(rhs_lower)])):
            lhs_lower = lhs_lower + 1
            rhs_lower = rhs_lower + 1
        # trim off the matching items at the end
        while ((lhs_lower < lhs_upper) and (rhs_lower < rhs_upper) and (lhsctx.codes[str(lhs_upper - 1)] == rhsctx.codes[str(rhs_upper - 1)])):
            lhs_upper = lhs_upper - 1
            rhs_upper = rhs_upper - 1
        if (lhs_lower == lhs_upper):
            while (rhs_lower < rhs_upper):
                rhsctx.modified[str(rhs_lower)] = True
                rhs_lower = rhs_lower + 1
        elif (rhs_lower == rhs_upper):
            while (lhs_lower < lhs_upper):
                lhsctx.modified[str(lhs_lower)] = True
                lhs_lower = lhs_lower + 1
        else:
            p_p = Myers.get_shortest_middle_snake(lhsctx, lhs_lower, lhs_upper, rhsctx, rhs_lower, rhs_upper, vectorU, vectorD)
            x = p_p['x']
            y = p_p['y']
            Myers.get_longest_common_subsequence(lhsctx, lhs_lower, x, rhsctx, rhs_lower, y, vectorU, vectorD)
            Myers.get_longest_common_subsequence(lhsctx, x, lhs_upper, rhsctx, y, rhs_upper, vectorU, vectorD)

    # Compare {@code lhs} to {@code rhs}.  Changes are compared from left
    # * to right such that items are deleted from left, or added to right,
    # * or just otherwise changed between them.
    # *
    # * @param   {string} lhs - The left-hand source text.
    # * @param   {string} rhs - The right-hand source text.
    @staticmethod
    def diff(lhs, rhs, options=None):
        encoder = MyersDiffEncoder()
        if (not hasattr(lhs,'__len__')):
            raise Exception('illegal argument \'lhs\'')
        if (not hasattr(rhs,'__len__')):
            raise Exception('illegal argument \'rhs\'')
        if not hasattr(options,'__getitem__'):
            options = {}
        settings = {**myers_diff_get_default_settings(),**options}
        lhsctx = encoder.encode(lhs,settings)
        rhsctx = encoder.encode(rhs,settings)
        # Myers.LCS(lhsctx, rhsctx)
        Myers.get_longest_common_subsequence(lhsctx, 0, lhsctx.length, rhsctx, 0, rhsctx.length, [None for i in range(0,4*(len(lhs)+len(rhs))+10)], [None for i in range(0,4*(len(lhs)+len(rhs))+10)] )
        # compare lhs/rhs codes and build a list of comparisons
        changes = []
        compare = 1 # that means lines not chars
        def _changeItem(item):
            # add context information
            def _lhs_get_part(n):
                return lhsctx._parts[n]
            def _rhs_get_part(n):
                return rhsctx._parts[n]
            item['lhs']['get_part'] = _lhs_get_part
            item['rhs']['get_part'] = _rhs_get_part
            if (compare == 0):
                # chars
                item['lhs']['length'] = item['lhs']['del']
                item['rhs']['length'] = item['rhs']['add']
            else:
                # words and lines
                item['lhs']['length'] = 0
                if (item['lhs']['del']):
                    # get the index of the second-last item being deleted
                    # plus its length, minus the start pos.
                    i = item['lhs']['at'] + item['lhs']['del'] - 1
                    part = lhsctx._parts[i]
                    item['lhs']['length'] = part['pos'] + 1 - lhsctx._parts[item['lhs']['at']]['pos']
                item['rhs']['length'] = 0
                if (item['rhs']['add']):
                    # get the index of the second-last item being added,
                    # plus its length, minus the start pos.
                    i = item['rhs']['at'] + item['rhs']['add'] - 1
                    part = rhsctx._parts[i]
                    item['rhs']['length'] = part['pos'] + 1 - rhsctx._parts[item['rhs']['at']]['pos']
            changes.append(item)
        Myers.compare_lcs(lhsctx, rhsctx, _changeItem)
        lhsctx.finish()
        rhsctx.finish()
        return changes

    # converts results formatted with lhs and rhs to a list with DiffItemKeep, DiffItemInsert, DiffItemRemove items
    @staticmethod
    def to_records(diff,a,b):
        results = []
        lastIndex = 0
        for diffObj in diff:
            results = [
                *results,
                *map(
                    lambda line: DiffItemKeep(line),
                    a[ lastIndex : diffObj['lhs']['at'] ]
                ),
                *map(
                    lambda line: DiffItemRemove(line),
                    a[ diffObj['lhs']['at'] : diffObj['lhs']['at'] + diffObj['lhs']['del'] ]
                ),
                *map(
                    lambda line: DiffItemInsert(line),
                    b[diffObj['rhs']['at'] : diffObj['rhs']['at'] + diffObj['rhs']['add'] ]
                )
            ]
            lastIndex = diffObj['lhs']['at'] + diffObj['lhs']['del']
        results = [
            *results,
            *map(
                lambda line: DiffItemKeep(line),
                a[lastIndex:]
            )
        ];
        return results





