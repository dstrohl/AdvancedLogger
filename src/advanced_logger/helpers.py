
class IndentHelper(object):
    def __init__(self, size=0, spaces=4, max_size=100, **kwargs):
        self.spaces = spaces
        self.max_size = max_size
        self.indent = size
        self.names = kwargs.copy()
        self.contexts = []

    def set(self, size):
        if isinstance(size, str):
            size = self.names[size]
        if size > self.max_size:
            size = self.max_size
        elif size < 0:
            size = 0
        self.indent = size
        return self

    def a(self, size=1):
        self.set(self.indent + size)
        return self

    def s(self, size=1):
        self.set(self.indent - size)
        return self

    @property
    def i(self):
        return str(self)

    def push(self, name, size=None):
        size = size or self.indent
        self.names[name] = size
        return self

    def pop(self, name):
        self.set(name)
        del self.names[name]
        return self

    def delete(self, name):
        del self.names[name]
        return self

    def clear(self):
        self.indent = 0
        self.names.clear()

    def __iadd__(self, other):
        self.a(other)
        return self

    def __isub__(self, other):
        self.s(other)
        return self

    def __str__(self):
        return ' ' * self.spaces * self.indent

    def __enter__(self):
        self.contexts.append(self.indent)
        self.a()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.set(self.contexts.pop())
        return False

    def __call__(self, *size, set=None):
        if set is not None:
            self.set(set)

        if size:
            self.a(size[0])
        return self

    def __eq__(self, other):
        return other == self.indent

    def __int__(self):
        return self.indent

    def __contains__(self, item):
        return item in self.names

    def __repr__(self):
        return 'IndentHelper: size: %s, saves: %r' % (self.indent, self.names)


class LazyFunc(object):
    def __init__(self, data, *funcs):
        self.data = data
        self.funcs = funcs
        self.run_count = 0
        self._run_out = _UNSET

    def run(self):
        if self._run_out is not _UNSET:
            return self._run_out
        self.run_count += 1
        tmp_data = self.data
        for f in self.funcs:
            if isinstance(f, list):
                if len(f) == 2:
                    tmp_data = tmp_data[f[0]: f[1]]
                elif len(f) == 1:
                    if isinstance(f[0], str):
                        tmp_data = tmp_data[f[0]]
                    else:
                        tmp_data = tmp_data[f[0]]
                else:
                    raise AttributeError('Invalid function reference: %r' % f)
            elif isinstance(f, str):
                tmp_data = getattr(tmp_data, f)
                if callable(tmp_data):
                    tmp_data = tmp_data()
            else:
                tmp_data = f(tmp_data)
        return tmp_data

    def __str__(self):
        return str(self.run())

    def __repr__(self):
        return repr(self.run())



class CounterDict(UserDict):

    def __init__(self, *args, _inc_total=True, **kwargs):
        self._inc_total = _inc_total
        super(CounterDict, self).__init__()
        self.max_key_length = 0
        if args:
            for a in args:
                if isinstance(a, dict):
                    self.update(a)
                else:
                    self[a] = 0
        self.update(kwargs)

    def __getitem__(self, item):
        if item not in self.data:
            self.max_key_length = max(self.max_key_length, len(item))
            self.data[item] = 0
        return self.data[item]

    def __setitem__(self, key, value):
        if isinstance(value, dict):
            self.update(value)
        else:
            if self._inc_total:
                total = self['total'] + value
                self.data['total'] = total
            value = self[key] + value
            self.data[key] = value

    def __iadd__(self, other):
        self.update(other)
        return self

    def __isub__(self, other):
        self.update(other, _sub=True)
        return self

    def update(self, other=None, _sub=False, **kwargs):
        if other:
            if isinstance(other, str):
                other = {other: 1}
            for key, value in other.items():
                if self._inc_total and key == 'total':
                    continue
                if _sub:
                    value *= -1
                self[key] = value
        if kwargs:
            self.update(kwargs, _sub=_sub)

    def __instancecheck__(self, instance):
        return instance is dict or instance is self.__class__

    def __len__(self):
        tmp_ret = len(self.data)
        if self._inc_total:
            return tmp_ret - 1
        return tmp_ret

    @property
    def total(self):
        return sum(self.data.values())

    def dump(self):
        tmp_ret = []
        max_val = str(max(self.data.values()))
        max_val_len = len(max_val)
        for key, value in self.data.items():
            key = key.ljust(self.max_key_length)
            value = str(value).rjust(max_val_len)
            tmp_ret.append(key + ' : ' + value)
        return '\n'.join(tmp_ret)






class LazyFunc(object):
    def __init__(self, data, *funcs):
        self.data = data
        self.funcs = funcs
        self.run_count = 0
        self._run_out = _UNSET

    def run(self):
        if self._run_out is not _UNSET:
            return self._run_out
        self.run_count += 1
        tmp_data = self.data
        for f in self.funcs:
            if isinstance(f, list):
                if len(f) == 2:
                    tmp_data = tmp_data[f[0]: f[1]]
                elif len(f) == 1:
                    if isinstance(f[0], str):
                        tmp_data = tmp_data[f[0]]
                    else:
                        tmp_data = tmp_data[f[0]]
                else:
                    raise AttributeError('Invalid function reference: %r' % f)
            elif isinstance(f, str):
                tmp_data = getattr(tmp_data, f)
                if callable(tmp_data):
                    tmp_data = tmp_data()
            else:
                tmp_data = f(tmp_data)
        return tmp_data

    def __str__(self):
        return str(self.run())

    def __repr__(self):
        return repr(self.run())


class MinMaxObj(object):
    def __init__(self, keep_first=True):
        self.min_value = sys.maxsize
        self.max_value = -sys.maxsize
        self.min_objs = []
        self.max_objs = []
        self.keep_first = keep_first

    def __call__(self, value, obj=None):
        if value < self.min_value:
            self.min_value = value
            self.min_objs.clear()
            self.min_objs.append(obj)

        elif value == self.min_value:
            self.min_objs.append(obj)

        if value > self.max_value:
            self.max_value = value
            self.max_objs.clear()
            self.max_objs.append(obj)
        elif value == self.max_value:
            self.max_objs.append(obj)

    def min(self, inc_ties=False):
        if inc_ties:
            return self.min_objs
        elif not self.min_objs:
            return None

        elif self.keep_first:
            return self.min_objs[0]
        else:
            return self.min_objs[-1]

    def max(self, inc_ties=False):
        if inc_ties:
            return self.max_objs
        elif not self.max_objs:
            return None
        elif self.keep_first:
            return self.max_objs[0]
        else:
            return self.max_objs[-1]

    @property
    def has_min_tie(self):
        return len(self.min_objs) > 1

    @property
    def has_max_tie(self):
        return len(self.max_objs) > 1


class PercentObj(object):
    """
    percentage handler, if the percentage is 12.4% to get back:

    12.4 = float(po)
    12 = int(po)
    12.4% = str(po)

    """

    def __init__(self, current=0, min_count=0, max_count=100, decimal_prec=2, min_perc=0,
                 inc_perc_char=True, return_1_based=False, counter_type=None,
                 max_perc = 100,
                 ):
        """

        @param current:
        @param min_count:
        @param max_count:
        @param decimal_prec:
        @param min_perc:
        @param max_perc:
            min / max perc are values that any reported percentages will always be over/under.
            These do not change the value of the base perc field.
            IF None, the percentage can return as a negative or above 100%
        @param inc_perc_char:
        @param return_1_based: will return values from 0.0 to 1.0 instead of 0 to 100.
        @param counter_as_float: Will force all counter items to float tyoe, otherwise all counter items will be rounded to the nearest int.
        """

        self.counter_type = counter_type
        self.decimal_prec = decimal_prec
        self.initial_current = current
        self.min_count = min_count
        self.max_count = max_count
        self.count_range = self.max_count - self.min_count
        if self.count_range <= 0:
            raise AttributeError('Min range must be lower than max range')
        if return_1_based and decimal_prec < 1:
            raise AttributeError('Decimal precision cannot be 0 if returning 1 based values')
        self.min_perc = min_perc
        self.max_perc = max_perc

        self.current_count = 0
        self.current_offset = min_count
        self.inc_perc_char = inc_perc_char
        self.return_1_based = return_1_based
        self._base_perc = None

        self.set(current)

    def dump(self):
        tmp_ret = [
            'Current Count: %r' % self.current_count,
            'Offset: %r' % self.current_offset,
            'Min Count: %r' % self.min_count,
            'Max Count: %r' % self.max_count,
            'Min Perc: %r' % self.min_perc,
            'Max Perc: %r' % self.max_perc,
            'Count Range: %r' % self.count_range,
            'Decimal Prec: %r' % self.decimal_prec,
            'Base Perc: %r' % self.base_perc,
            'Final Perc: %r' % self.perc,
        ]
        return '\n'.join(tmp_ret)

    def clear(self):
        self.set(self.initial_current)

    """
    def make_perc(self, count):
        if isinstance(count, self.__class__):
            return count.perc / self.item_perc
        return Decimal(count) / self.item_perc
    """
    @property
    def base_perc(self):
        """
        Will return the percentage in base 1 format (i.e. from 0.0 to 1.0
        Note: will not round to the precision decimal places.
        @return:
        """
        if self.count_range == 0:
            return 0.0
        else:
            return self.current_offset / self.count_range

    @property
    def started(self):
        return self.base_perc > 0.0

    @property
    def finished(self):
        return self.base_perc >= 1.0

    @property
    def running(self):
        return self.started and not self.finished

    @property
    def perc(self):
        """
        will return the percentage in either base 1 or base 100 format depending on the setting of "return_1_based"
        will round to the number of decimal precision places based on "decimal_prec"
        @return:
        """
        return self._perc()

    def _perc(self, force_100_based=False):
        tmp_ret = self.base_perc * 100
        tmp_ret = minmax(tmp_ret, self.min_perc, self.max_perc)
        tmp_ret = round(tmp_ret, self.decimal_prec)

        if self.return_1_based and not force_100_based:
            tmp_ret = tmp_ret / 100

        return tmp_ret

    def set_perc(self, perc_in):
        """
        Will set the value based on a percentage.  i.e. if your range is 0-50, and you set_perc(50), your current value will be set to 25
        @param perc_in: either a 1 or 100 based percentage based on the setting of "return_1_based"
        @return:
        """
        if isinstance(perc_in, self.__class__):
            perc_in = perc_in.base_perc
        elif not self.return_1_based:
            perc_in = perc_in / 100
        self._set_perc(perc_in)

    def _set_perc(self, perc_in):
        self._base_perc = None
        new_offset = self.count_range * perc_in
        new_count = self.min_count + new_offset
        self.set(new_count)

    def add_perc(self, perc_in):
        """
        Will set the value based on adding a percentage to the current percentage.
        i.e. if your range is 0-50, and your current percentage is 25% and you add_perc(25), your current value will be set to 25
        @param perc_in: either a 1 or 100 based percentage based on the setting of "return_1_based"
        @return:
        """
        if isinstance(perc_in, self.__class__):
            perc_in = perc_in.base_perc
        elif not self.return_1_based:
            perc_in = perc_in / 100
        new_perc = perc_in + self.base_perc
        self._set_perc(new_perc)

    def sub_perc(self, perc_in):
        """
        Will set the value based on adding a percentage to the current percentage.
        i.e. if your range is 0-50, and your current percentage is 25% and you sub_perc(25), your current value will be set to 0
        @param perc_in: either a 1 or 100 based percentage based on the setting of "return_1_based"
        @return:
        """
        if isinstance(perc_in, self.__class__):
            perc_in = perc_in.base_perc
        elif not self.return_1_based:
            perc_in = perc_in / 100
        new_perc = self.base_perc - perc_in
        self._set_perc(new_perc)

    def _get_other(self, other):
        if isinstance(other, (int, float)):
            tmp_ret = other
        else:
            tmp_ret = other.current_count

        if self.counter_type is not None:
            if self.counter_type is int:
                tmp_ret = int(round(tmp_ret))
            else:
                tmp_ret = self.counter_type(tmp_ret)

        return tmp_ret

    def set(self, count):
        """
        Will set the current count to x (assumes that the count is based on the offset.)
        @param count:
        @return:
        """
        count = self._get_other(count)
        self._base_perc = None
        if self.min_perc is not None:
            count = max(self.min_count, count)
        if self.max_perc is not None:
            count = min(self.max_count, count)
        self.current_count = count
        self.current_offset = count - self.min_count

    def add(self, count):
        """
        Will add x to the current count.
        @param count:
        @return:
        """
        count = self._get_other(count)
        self.set(count + self.current_count)

    def sub(self, count):
        """
        Will subtract x from the current count.
        @param count:
        @return:
        """
        count = self._get_other(count)
        self.set(self.current_count - count)

    def __call__(self, count):
        """
        will add x to the current count
        @param count:
        @return:
        """
        self.set(count)

    def __iadd__(self, other):
        self.add(other)
        return self

    def __isub__(self, other):
        self.sub(other)
        return self

    def __float__(self):
        return float(self.perc)

    def __int__(self):
        return round(self._perc(force_100_based=True))

    def __str__(self):
        tmp_ret = str(self._perc(force_100_based=True))
        if '.' in tmp_ret:
            tmp_ret = tmp_ret.rstrip('0')
            tmp_ret = tmp_ret.rstrip('.')
        if self.inc_perc_char:
            tmp_ret += '%'
        return tmp_ret

    def __repr__(self):
        return f'PercentageObj({self.current_count} in {self.min_count}<->{self.max_count}) = {self.perc}%'

    def __bool__(self):
        return self.current_offset > 0

    def __compare__(self, other):
        compare_with = self.base_perc
        if isinstance(other, self.__class__):
            other = other.base_perc
        if other == compare_with:
            return 0
        elif other > compare_with:
            return -1
        else:
            return 1

    def __eq__(self, other):
        return self.__compare__(other) == 0

    def __lt__(self, other):
        return self.__compare__(other) == -1

    def __le__(self, other):
        return self.__compare__(other) < 1

    def __gt__(self, other):
        return self.__compare__(other) == 1

    def __ge__(self, other):
        return self.__compare__(other) > -1



def deslugify(text, delim='_-.', case='title'):
    """
    generates a title or proper case text string.
    :param text:
    :param delim: a string used to delimit words
    :param case: ['lower'/'upper'/'title'/'sentence']
    """
    for char in delim:
        text = text.replace(char, ' ')
    if case == 'title':
        text = text.title()
    elif case == 'lower':
        text = text.lower()
    elif case == 'upper':
        text = text.upper()
    elif case == 'capitalize':
        text = text.capitalize()
    return text



def slugify(text, delim='_', case='lower', allowed=None, punct_replace='', encode=None):
    """
    generates a simpler text string.

    :param text:
    :param delim: a string used to delimit words
    :param case: ['lower'/'upper'/'no_change']
    :param allowed: a string of characters allowed that will not be replaced.  (other than normal alpha-numeric which
        are never replaced.
    :param punct_replace: a string used to replace punction characters, if '', the characters will be deleted.
    :param encode: Will encode the result in this format.
    :return:
    """
    punct = '[\t!"#$%&\'()*\-/<=>?@\[\\\]^_`{|},.]+'
    if allowed is not None:
        for c in allowed:
            punct = punct.replace(c, '')

    result = []

    for word in text.split():
        word = normalize('NFKD', word)
        for c in punct:
            word = word.replace(c, punct_replace)
        result.append(word)

    delim = str(delim)
    # print('sluggify results: ', result)
    text_out = delim.join(result)

    if encode is not None:
        text_out.encode(encode, 'ignore')

    if case == 'lower':
        return text_out.lower()
    elif case == 'upper':
        return text_out.upper()
    else:
        return text_out



def make_list(in_obj, sep=None):
    """
    Will take in an object, and if it is not already a list or other iterables, it will convert it to one.

    This is helpful when you dont know if someone will pass a single string, or a list of strings (since strings
    are iterable you cant just assume)

    This uses the :py:func:`is_iterable` function from this module.

    :param in_obj: list, string, or other iterable.
    :return: a list object.
    :rtype: list
    """
    if in_obj is None:
        return []
    elif isinstance(in_obj, dict):
        return [in_obj]
    elif isinstance(in_obj, str):
        if sep is not None:
            return in_obj.split(sep)
        else:
            return [in_obj]
    elif is_iterable(in_obj):
        return in_obj
    else:
        return [in_obj]





def minmax(value, min_val=None, max_val=None):
    if min_val is None and max_val is None:
        return value
    if min_val is None:
        return min(value, max_val)
    if max_val is None:
        return max(value, min_val)
    return min(max_val, max(value, min_val))
