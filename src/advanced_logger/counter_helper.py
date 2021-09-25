"""

This utility provides some advanced counting functions allowing for easier counting and incrementing.

"""
__author__ = 'strohl'
__version__ = '0.9'
__status__ = 'Testing'

import decimal
from collections import OrderedDict
import sys
from .helpers import make_list, slugify
# from advanced_counter.helpers import make_list, _UNSET, slugify, PercentObj
import logging

log = logging.getLogger(__name__)

__all__ = ['NamedCounter', 'Counter', 'CounterSet']


class AdvCounter(object):
    value = 0
    min_value = 0
    max_value = 0
    increment_type = 'dict'
    increment_length = None
    increment_index = None

    def __init__(self,
                 name=None,
                 value=0,
                 key=None,
                 obj=None,
                 min_counter=None,
                 max_counter=None,
                 rollover=False,
                 increment_by=1,
                 perc_decimal=None,
                 force_type=int,
                 no_scan=False,
                 ):
        """
        @param name: The name that the counter uses.  (must be set to use with a counterset)
        @param value: The initial value for this counter.
        @param key: defaults to a slugified version of the name.  This is the key that is used if this is used as part of a CounterSet.
        @param obj: Can be passed, this is only a holding var for an object that can be returned if this is returned as a dict.  Nothing is done with this obj.
        @param min_counter: if set, the value will never go below this setting (defaults to 0)
        @param max_counter: if set, the value will never go above this value (defaults to sys.maxsize)
        @param rollover: If true, will start over at the min_counter once the max_counter is reached, and vice versa (for reverse)
            NOTE: Rollover only happens with addition/subtraction of values, it will not happen with setting a value, multiplying or dividing it.
                in those cases, the value will be set to the max (or min) value.
        @param increment_by: any of the following: (defaults to 1)
             int: will add that int to each iteration by default.
             list or set of values:
                will iterate across the list and use the value to handle that process.
                if a number is passed in the, that index in the list will be used (0 based).
                    (so, if a list such as [1,2,4,8] is passed in the inc by field, ac.add(3) will increment by 8)
                    note if a value that is higher than the size of the list is passed, an IndexError will be raised.
                    normally, at the end of the list, it will return to the start of the list for the next entry.
                    if the last entry is '...', the prior entry will be used for any more increments

             dict with keys and values of the above.
                will use the key to lookup the increment_by value.
                dict can have a '_default_' key that will be used if a key is not specified.
                    note that if the key is not found in the dict, a KeyError will be raised.
            Note: with dict and list increment_by operations, you can force a value by using ac.set(234, force=True)
            note: dict and lists have values scanned to make sure they are numeric unless the 'no_scan' parameter is set to True,
                any objects that are not of a type of int, float, or decimal will rase a TypeError.
        @param no_scan: will skip scanning the increment_by values (for large lists and dicts, this can save init time)
        @param perc_decimal: [defaults to 0] the number of decimal places that any percentage will use.
            note, percentages only available if max_counter is set.  otherwise, calling perc will return 0.0
        @param force_type: [def: int]  Will force the value to in int, float, or decimal. (or whatever other object).
            note, this is called before calculations, so if the base value is a float and we will be multiplying by a float.
            note this is also called after division calcs, so if you are doing ac(10) / ac(3), you will end up with ac(3)

        """
        self.increment_by = increment_by
        self.key = key or slugify(name)
        self.obj = obj
        self.name = name
        self.min_counter = min_counter or 0
        self.max_counter = max_counter or sys.maxsize
        self.rollover = rollover
        self.perc_decimal = perc_decimal
        self.force_type = force_type

        if isinstance(increment_by, (list, tuple)):
            if not no_scan:
                for index, value in enumerate(increment_by):
                    if not isinstance(value, (int, float, decimal.Decimal)):
                        raise TypeError('Invalid value passed (%r) in iterable index %r' % (value, index))

            self.increment_type = 'list'
            self.increment_length = len(increment_by)
            self.increment_index = AdvCounter(
                name=name+'_inc_index',
                value=0,
                min_counter=0,
                max_counter=self.increment_length-1,
                rollover=rollover,
                increment_by=1
            )
        elif isinstance(increment_by, dict):
            self.increment_type = 'dict'
            if not no_scan:
                for key, value in increment_by.items():
                    if not isinstance(value, (int, float, decimal.Decimal)):
                        raise TypeError('Invalid value passed (%r) in dictionary key %r' % (value, key))

        elif isinstance(increment_by, str):

            if increment_by[0]:

            self.increment_type = 'str'
        else:
            self.increment_type = 'int'

        self.set(value)
    def scan_values(self, vals_in):

        for v in vals_in:
            if not isinstance(v, (int, float, decimal.Decimal)):
                raise TypeError('Value ')

    def get_increment(self, increment=None):
        if self.increment_type == 'list':

            return increment

        elif self.increment_type == 'dict':
            try:
                return self.increment_by[increment]
            except KeyError:
                return self.increment_by['_default_']
        else:
            return self.increemnt

        if increment_index is None:


    def clear(self):
        self.value = self.min_counter

    def get(self, field_name):
        return getattr(self, field_name)

    def add(self, value=None):
        if self.increment_type == 'int':
            if value is None:
                value = self.increment_by
            self.value += int(value)
            if self.value > self.max_counter:
                if self.rollover:
                    while self.value > self.max_counter:
                        self.value = self.min_counter + (self.value - self.max_counter)
                else:
                    self.value = self.max_counter
        else:
            if value is None:
                value = 1
            index = self.increment_index.add(value)
            add_value = self.increment_by[index]
            self.value += add_value
            if self.value > self.max_counter:
                self.value = self.max_counter
        return self.value

    def sub(self, value=_UNSET):
        if self.increment_type == 'int':
            if value is _UNSET:
                value = self.increment_by
            if value is None:
                value = self.value / 2
            self.value -= int(value)
            if self.value < self.min_counter:
                if self.rollover:
                    while self.value < self.min_counter:
                        tmp_diff = self.min_counter - self.value
                        self.value = self.max_counter - tmp_diff
                else:
                    self.value = self.min_counter
        else:
            if value is _UNSET or value is None:
                value = 1
            index = self.increment_index.sub(value)
            sub_value = self.increment_by[index]
            self.value -= sub_value
            if self.value < self.min_counter:
                self.value = self.min_counter
        return self.value

    def set(self, value=None, offset=1):
        if self.increment_type == 'int':
            self.value = int(value)
        else:
            if value is None:
                self.increment_index.add(offset)
            self.value = self.increment_by[int(self.increment_index)]

        if self.value > self.max_counter:
            self.value = self.max_counter
        elif self.value < self.min_counter:
            self.value = self.min_counter
        return self.value

    def __iadd__(self, other):
        self.add(other)
        return self

    def __isub__(self, other):
        self.sub(other)
        return self

    def __int__(self):
        return self.value

    def __call__(self, inc_name=True, inc_value=True, inc_obj=False, as_dict=False):
        if not as_dict:
            tmp_ret = []
            if inc_name:
                tmp_ret.append(self.name)
            if inc_value:
                tmp_ret.append(self.value)
            if inc_obj:
                tmp_ret.append(self.obj)
            if len(tmp_ret) == 1:
                tmp_ret = tmp_ret[0]
        else:
            tmp_ret = {}
            if inc_name:
                tmp_ret['name'] = self.name
            if inc_value:
                tmp_ret['value'] = self.value
            if inc_obj:
                tmp_ret['obj'] = self.obj
            if len(tmp_ret) == 1:
                tmp_field = list(tmp_ret.keys())[0]
                tmp_ret = tmp_ret[tmp_field]
            tmp_ret = {self.name: tmp_ret}
        return tmp_ret

    def __str__(self):
        return self.name

    def __repr__(self):
        tmp_ret = '%s (%s)' % (self.name, self.value)
        if self.obj is not None:
            tmp_ret += ' [obj]'

        if self.min_counter > 0 and self.max_counter < sys.maxsize:
            tmp_ret += ' (%s <-> %s)' % (self.min_counter, self.max_counter)
        elif self.min_counter > 0:
            tmp_ret += ' (%s <-> [any])' % self.min_counter
        elif self.max_counter < sys.maxsize:
            tmp_ret += ' ([any] <-> %s)' % self.max_counter

        if self.rollover:
            tmp_ret += ' [rollover]'

        return tmp_ret



class NamedCounter(object):
    counters = None
    def_counter_kwargs = None
    locked = False

    def __init__(self, *args, locked=False, min_counter=0, max_counter=None, rollover=False, increment_by=1, **kwargs):
        self.def_counter_kwargs = dict(
            value=min_counter,
            min_counter=min_counter,
            max_counter=max_counter,
            rollover=rollover,
            increment_by=increment_by,
        )
        self.counters = OrderedDict()

        self.new('__base__')

        for arg in args:
            self.new(arg)
        
        for key, value in kwargs.items():
            if isinstance(value, int):
                self.new(key, value)
            else:
                self.new(key, obj=value)

        self.locked = locked

        self.__initialised = True

    def new(self, name, value=None, **kwargs):

        tmp_kwargs = self.def_counter_kwargs.copy()
        tmp_kwargs.update(kwargs)
        if value is not None:
            tmp_kwargs['value'] = value

        tmp_counter = AdvCounter(name, **tmp_kwargs)

        self.counters[name] = tmp_counter
        return tmp_counter

    def get(self, name='__base__', obj=None):
        if name not in self:
            if self.locked:
                raise KeyError('cannot add %s, counter locked with fields: %r' % (name, list(self.counters.keys())))
            return self.new(name, obj=obj)
        else:
            return self.counters[name]

    def sub(self, names='__base__', value=_UNSET, obj=None):
        tmp_ret = []
        for name in make_list(names):
            tmp_item = self.get(name, obj=None)
            tmp_ret.append(tmp_item.sub(value))
        if len(tmp_ret) == 1:
            return tmp_ret[0]
        else:
            return tmp_ret

    def add(self, names='__base__', value=_UNSET, obj=None):
        tmp_ret = []
        for name in make_list(names):
            tmp_item = self.get(name, obj=None)
            tmp_ret.append(tmp_item.add(value))
        if len(tmp_ret) == 1:
            return tmp_ret[0]
        else:
            return tmp_ret

    def set(self, names='__base__', value=None, offset=1, obj=None):
        tmp_ret = []
        for name in make_list(names):
            tmp_item = self.get(name, obj=None)
            tmp_ret.append(tmp_item.set(value, offset=offset))
        if len(tmp_ret) == 1:
            return tmp_ret[0]
        else:
            return tmp_ret

    def remove(self, *names):
        for name in names:
            self.get(name)
            del self.counters[name]

    def clear(self, *names):
        if names:
            for name in names:
                self.get(name).clear()
        else:
            for item in self.counters.values():
                item.clear()

    def clear_all(self):
        if self.locked:
            self.clear()
        else:
            self.counters.clear()
            self.new('__base__')

    def recs(self, order_by=None, order_reversed=False):
        tmp_items = list(self.counters.keys())
        if order_by:
            tmp_items.sort(key=lambda key: self.counters[key].get(order_by), reverse=order_reversed)
        for item in tmp_items:
            tmp_rec = self.counters[item]
            if tmp_rec.name != '__base__':
                yield tmp_rec

    def items(self, inc_name=True, inc_value=False, inc_obj=False, order_by=None, as_dict=False, order_reversed=False):
        if not inc_value and not inc_obj and as_dict:
            raise AttributeError('as_dict requires at least one of "inc_value" or "inc_obj"')
        if as_dict:
            tmp_ret = {}
        else:
            tmp_ret = []

        for tmp_rec in self.recs(order_by=order_by, order_reversed=order_reversed):
            if tmp_rec.name != '__base__':
                if as_dict:
                    tmp_ret.update(tmp_rec(inc_name=inc_name, inc_value=inc_value, inc_obj=inc_obj, as_dict=as_dict))
                else:
                    tmp_ret.append(tmp_rec(inc_name=inc_name, inc_value=inc_value, inc_obj=inc_obj, as_dict=as_dict))
        return tmp_ret

    def __iter__(self):
        for item in self.items():
            yield item

    def sum(self):
        return sum(self.items(inc_value=True, inc_name=False, inc_obj=False))

    def _min_max(self, order_reversed, inc_ties, **kwargs):
        tmp_ret = []
        tmp_value = None
        for item in self.recs(order_by='value', order_reversed=order_reversed):
            if inc_ties:
                if tmp_value is None:
                    tmp_value = item.value
                else:
                    if tmp_value != item.value:
                        return tmp_ret
                tmp_ret.append(item(**kwargs))
            else:
                return item(**kwargs)
        return tmp_ret

    def min(self, inc_name=True, inc_value=False, inc_obj=False, inc_ties=False):
        return self._min_max(inc_ties=inc_ties, inc_name=inc_name, inc_value=inc_value, inc_obj=inc_obj,
                             order_reversed=False)

    def max(self, inc_name=True, inc_value=False, inc_obj=False, inc_ties=False):
        return self._min_max(inc_ties=inc_ties, inc_name=inc_name, inc_value=inc_value, inc_obj=inc_obj,
                             order_reversed=True)

    def __call__(self, name='__base__'):
        return self.get(name).value

    def __contains__(self, item):
        return item in self.counters

    def __iadd__(self, other):
        self.counters['__base__'].add(other)
        return self

    def __isub__(self, other):
        self.counters['__base__'].sub(other)
        return self

    def __int__(self):
        return self.counters['__base__'].value

    def __getattr__(self, item):
        try:
            return self.get(item)
        except KeyError:
            raise AttributeError('%s not an attribute' % item)

    def __setattr__(self, key, value):
        if '_NamedCounter__initialised' not in self.__dict__:  # this test allows attributes to be set in the __init__ method
            super(NamedCounter, self).__setattr__(key, value)
        elif key in self.__dict__:       # any normal attributes are handled normally
            super(NamedCounter, self).__setattr__(key, value)
        else:
            try:
                self.set(key, value)
            except KeyError:
                raise AttributeError('%s not an attribute' % key)

    def __len__(self):
        return len(self.counters) - 1

    def dump(self, sep='\n'):
        tmp_ret = []
        for x in self.counters.values():
            tmp_ret.append(repr(x))

        if sep is None:
            return tmp_ret
        else:
            return sep.join(tmp_ret)

    def __repr__(self):
        return 'NamedCounter: %s objects' % len(self)


class Counter(object):

    def __init__(self, name=None, value=0, key=None, obj=None, min_counter=0, max_counter=None, rollover=False,
                 increment_by=1, perc_decimal=0, call_every=None, call_func=None, call_in_class=None, description=None):
        """
        @param name: The name that the counter uses.  (must be set to use with a counterset)
        @param value: The initial value for this counter.
        @param key: defaults to a slugified version of the name.  This is the key that is used if this is used as part of a CounterSet.
        @param obj: Can be passed, this is only a holding var for an object that can be returned if this is returned as a dict.  Nothing is done with this obj.
        @param min_counter:
        @param max_counter:
        @param rollover: If true, will start over at the min_counter once the max_counter is reached, and vice versa (for reverse)
            NOTE: Rollover only happens with addition/subtraction of values, it will not happen with setting a value.
                in those cases, the value will be set to the max (or min) value.
        @param increment_by: (defaults to 1) the number that this increments by if a value is not passed. (for add/sub)
        @param perc_decimal: [defaults to 0] the number of decimal places that any percentage will use.
            note, percentages only available if max_counter is set.  otherwise, calling perc will return 0.0
        @param call_every: Will call every x records,
            if None, will call based on the following:
                0-10 records, every record
                11-100 records, every 10 records%
                101-500 records, every 20 records
                500-1000 records every 100 records%
                1001-5000 records, every 500 records
                5001+ records, every 1000 records%
                if no max_count setting, will call every 100 records
            if an integer, will call every x

        """
        if isinstance(name, int):
            value = name
            name = None

        self.min_counter = min_counter
        self.max_counter = max_counter or sys.maxsize
        self.description = description

        self._perc = None

        self.increment_by = increment_by
        self.value = 0
        self.init_value = value
        self.min_value = self.value
        self.max_value = self.value

        self.call_in_class = call_in_class
        self.call_every = call_every
        self.call_func = call_func
        self.call_counter = None
        self.call_countdown = self.call_counter

        self.name = name

        if key is None and name is not None:
            self.key = slugify(name)
        else:
            self.key = key

        self.obj = obj
        self.rollover = rollover
        self.perc_decimal = perc_decimal

        self.locked = False

        self.set_max(max_counter, value)

    def set_max(self, max_counter, value=None):
        self.max_counter = max_counter or sys.maxsize

        if self.max_counter != sys.maxsize:
            self._perc = PercentObj(min_count=self.min_counter, max_count=self.max_counter,
                                    decimal_prec=self.perc_decimal)
        else:
            self._perc = None

        if self.call_func is not None:
            if self.call_every is None:
                """
                0-10 records, every record
                11-100 records, every 10 records%
                101-500 records, every 20 records
                500-1000 records every 100 records%
                1001-5000 records, every 500 records
                5001+ records, every 1000 records%
                if no max_count setting, will call every 100 records

                """
                if self.max_counter == sys.maxsize:
                    self.call_counter = 100
                elif self.max_counter <= 10:
                    self.call_counter = 1
                elif self.max_counter <= 100:
                    self.call_counter = 10
                elif self.max_counter <= 500:
                    self.call_counter = 20
                elif self.max_counter <= 1000:
                    self.call_counter = 100
                elif self.max_counter <= 5000:
                    self.call_counter = 500
                else:
                    self.call_counter = 1000
            else:
                self.call_counter = self.call_every
            # log.debug('Setting the call every function to call every %s' % self.call_counter)
        self.call_countdown = self.call_counter

        if value is None:
            self.set(self.value)
        else:
            self.set(value)

    @property
    def perc(self):
        if self._perc is None:
            raise AttributeError('Percentage is not currently set')
        return self._perc

    def lock(self):
        self.locked = True

    def unlock(self):
        self.locked = False

    def clear(self, force=False):
        if self.locked and not force:
            return
        self.value = self.init_value
        self.clear_min_max(force=force)
        if self._perc is not None:
            self._perc.set(self.value)

    def clear_min_max(self, force=False):
        if self.locked and not force:
            return
        self.min_value = self.value
        self.max_value = self.value

    def add(self, value=_UNSET):
        if self.locked:
            return
        if value is _UNSET:
            value = self.increment_by
        if value is None:
            value = self.value
        self.value += int(value)
        if self.max_counter is not None:
            if self.value > self.max_counter:
                if self.rollover:
                    while self.value > self.max_counter:
                        self.value = self.min_counter + (self.value - self.max_counter) -1
                else:
                    self.value = self.max_counter
        self._update()
        return self.value

    def sub(self, value=_UNSET):
        if self.locked:
            return
        if value is _UNSET:
            value = self.increment_by

        if value is None:
            value = self.value / 2

        self.value -= int(value)
        if self.min_counter is not None:
            if self.value < self.min_counter:
                if self.rollover:
                    while self.value < self.min_counter:
                        tmp_diff = self.min_counter - self.value
                        self.value = self.max_counter - tmp_diff + 1
                else:
                    self.value = self.min_counter
        self._update()
        return self.value

    def set(self, value):
        if self.locked:
            return
        self.value = int(value)

        if self.value > self.max_counter:
            self.value = self.max_counter
        elif self.min_counter is not None and self.value < self.min_counter:
            self.value = self.min_counter
        self._update()
        return self.value

    def _update(self):
        if self.call_countdown is not None:
            self.call_countdown -= 1
            if self.call_countdown <= 0:
                self.call_countdown = self.call_counter
                # if self.call_in_class is None:
                self.call_func(self)
                # else:
                #     self.call_func(self.call_in_class, self)

        self.min_value = min(self.min_value, self.value)
        self.max_value = max(self.max_value, self.value)
        if self._perc is not None:
            self._perc.set(self.value)

    def __iadd__(self, other):
        self.add(other)
        return self

    def __isub__(self, other):
        self.sub(other)
        return self

    def __int__(self):
        return self.value

    def __call__(self, add_val=_UNSET, sub_val=_UNSET, set_val=_UNSET):
        if add_val is _UNSET and sub_val is _UNSET and set_val is _UNSET:
            add_val = self.increment_by
        if add_val is not _UNSET:
            self.add(add_val)
        if sub_val is not _UNSET:
            self.sub(sub_val)
        if set_val is not _UNSET:
            self.set(set_val)
        return self.value

    def format(self, format_spec=None, pad_field=None, pad_field_size=None, pad_field_dir='l', line_indent=0, **kwargs):
        """
        @param format_spec:
        uses keys:
            {value}
            {perc} (automatically includes "%")
            {obj}
            {min_value} (this is the lowest that the value ever was)
            {max_value} (this is the highest that the value ever was)
            {min_counter}
            {max_counter}
            {name}
            {key}
            {description}
            + any kwargs passed.

        default formats:
            if name set: starts with '{name} : '
            if max_counter set: ends with  ' ({perc})
            if there is a description: ends with -- description
        @return:
        """
        if format_spec is None:
            format_spec = ''
            if self.name is not None:
                format_spec += '{name} : '
            format_spec += '{value}'
            if self._perc is not None:
                format_spec += ' ({perc})'
            if self.description:
                format_spec += ' -- {description}'

        if '{perc}' in format_spec and self._perc is None:
            raise KeyError('Percentage is not available for format: %r' % format_spec)

        if ('{name}' in format_spec or '{key}' in format_spec) and self.name is None:
            raise KeyError('Counter Name is not available for format: %r' % format_spec)

        if '{description}' in format_spec and not self.description:
            raise KeyError('Counter Description is not available for format: %r' % format_spec)

        tmp_dict = self.get_data(as_dict=True)
        tmp_dict.update(**kwargs)
        if pad_field is not None and pad_field_size is not None:
            pad_data = str(tmp_dict[pad_field])
            if pad_field_dir in '<r':
                pad_data = pad_data.ljust(pad_field_size)
            elif pad_field_dir in '>l':
                pad_data = pad_data.rjust(pad_field_size)
            else:
                pad_data = pad_data.center(pad_field_size)
            tmp_dict[pad_field] = pad_data
        tmp_ret = format_spec.format(**tmp_dict)
        if line_indent:
            line_indent = ''.ljust(line_indent, ' ')
            tmp_ret = line_indent + tmp_ret
        return tmp_ret

    def get_data(self, *field_names, as_dict=False):
        if not field_names:
            field_names = ['name', 'key', 'value', 'perc', 'obj', 'min_value', 'max_value', 'min_counter', 'max_counter', 'description']
            if self._perc is None:
                field_names.remove('perc')
            if not self.description:
                field_names.remove('description')
            if not self.name:
                field_names.remove('name')
            if not self.key:
                field_names.remove('key')
        if not as_dict:
            tmp_ret = []
            for fn in field_names:
                tmp_ret.append(getattr(self, fn))
        else:
            tmp_ret = {}
            for fn in field_names:
                tmp_ret[fn] = getattr(self, fn)

        return tmp_ret

    def __str__(self):
        return self.format()

    def __repr__(self):
        tmp_ret = '%s (%s)' % (self.name, self.value)
        if self.obj is not None:
            tmp_ret += ' [obj]'

        if self.min_counter > 0 and self.max_counter < sys.maxsize:
            tmp_ret += ' (%s <-> %s)' % (self.min_counter, self.max_counter)
        elif self.min_counter > 0:
            tmp_ret += ' (%s <-> [any])' % self.min_counter
        elif self.max_counter < sys.maxsize:
            tmp_ret += ' ([any] <-> %s)' % self.max_counter

        if self.rollover:
            tmp_ret += ' [rollover]'

        return tmp_ret

    def __bool__(self):
        return bool(self.value)

    def __compare__(self, other):
        compare_with = self.value
        other = int(other)
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

    def __len__(self):
        return 2


class CounterSet(object):
    counters = None
    def_counter_kwargs = None
    locked = False

    def __init__(self, *args, locked=False, min_counter=0, max_counter=None, rollover=False, increment_by=1,
                 perc_decimal=None, **kwargs):
        self.def_counter_kwargs = dict(
            value=min_counter,
            min_counter=min_counter,
            max_counter=max_counter,
            rollover=rollover,
            increment_by=increment_by,
            perc_decimal=perc_decimal,
        )
        self.counters = OrderedDict()
        self.pending_counters = {}

        for arg in args:
            self.new(arg)

        for key, value in kwargs.items():
            if isinstance(value, int):
                self.new(key, value)
            elif isinstance(value, dict):
                self.new(key, **value)
            elif isinstance(value, str):
                self.new(key, name=value)

        self.locked = locked

        self.__initialised = True

    def lock(self, *keys):
        if not keys:
            self.locked = True
            keys = self.counters.keys()

        for c in keys:
            self.counters[c].lock()

    def unlock(self, *keys):
        if not keys:
            self.locked = False
            keys = self.counters.keys()

        for c in keys:
            self.counters[c].unlock()

    def set_max(self, from_key, to_key):
        tmp_val = int(self[from_key])
        self[to_key].set_max(tmp_val)

    def new(self, key, value=None, force=False, **kwargs):
        """
        add new counter, this can be called in various ways:
            .new([key, value])
            .new(key, value)
            .new(CounterObj)
            .new(key, value, name=xxx, <other counter args>)
            .new(key)

        @param key:
        @param value:
        @param force: if False, this will raise an AttribueError if the name was already used.
        @param kwargs:
        @return:
        """

        if isinstance(key, str):
            tmp_kwargs = self.def_counter_kwargs.copy()
            tmp_kwargs.update(kwargs)
            if value is not None:
                tmp_kwargs['value'] = value
            if 'name' not in tmp_kwargs:
                tmp_kwargs['name'] = key
            else:
                tmp_kwargs['key'] = key

            key = Counter(**tmp_kwargs)
        elif isinstance(key, (list, tuple)):
            if value is not None:
                raise AttributeError('Invalid key/value passed: %s/%s' % (key, value))
            tmp_kwargs = self.def_counter_kwargs.copy()
            tmp_kwargs['value'] = key[1]
            tmp_kwargs['name'] = key[0]
            key = Counter(**tmp_kwargs)
        elif not isinstance(key, Counter):
            raise AttributeError('Invalid key passed: %r' % key)

        if not key.key:
            raise AttributeError('Counter object must have key/name attr to use in a CounterSet')
        if key.key in self and not force:
            raise AttributeError('Key %r already exists in CounterSet' % key.key)

        self.counters[key.key] = key
        return key

    def get(self, key):
        return self.counters[key]

    def remove(self, *keys):
        if self.locked:
            return
        for key in keys:
            if key in self.counters:
                if not self.counters[key].locked:
                    del self.counters[key]

    def clear(self, *keys):
        if self.locked:
            return
        if not keys:
            keys = self.counters.keys()
        for key in keys:
            self.get(key).clear()

    def clear_all(self):
        if self.locked:
            return

        self.counters.clear()

    def __str__(self):
        return self.report()

    def report(self, header=None, footer=None, justify_name=None,
               line_indent=None, counters=None, line_format=None, **kwargs):
        """
        @param header:
        @param footer:
            header / footer formatting options inc:
                {num_counters}
                {default_min}
                {default_max}
                {value_sum}
                {value_max}
                {value_min}
                {<counter_name>.<counter_format_option>}
                + any kwargs passed
        @param format:
        @param counters: if None, all counters are passed, otherwise this list of counters is returned.
        @param justify_name: one of the following:
            None: will not justify the name field
            '<': will justify left based on the length of the longest name
            '>': will justify right based on the length of the longest name
        @param line_indent:  this number is converted to a space string, which is then passed to the lines as "indent"
                (otherwise an "indent" string is passed with no contents)
        @param line_format:
            default with max_counter = "{indent}{name} : {value} ({perc})
            default without max_counter = "{indent}{name} : {value}
        @param kwargs: These are passed to the formatting for the lines as well as the header/footer.
        @return:
        """
        tmp_line_formating_dict = kwargs.copy()
        tmp_line_formating_dict['pad_field'] = None
        tmp_line_formating_dict['pad_field_size'] = None
        tmp_line_formating_dict['pad_field_dir'] = justify_name

        if counters is None:
            counters = self.counters.keys()
        else:
            counters = make_list(counters)

        if justify_name is not None:
            tmp_line_formating_dict['pad_field'] = 'name'
        tmp_pad_size = 0
        all_value_min = 0
        all_value_max = 0
        all_value_sum = 0

        if justify_name is not None or header or footer:
            for c in counters:
                c_rec = self.counters[c]
                tmp_pad_size = max(tmp_pad_size, len(c_rec.name))
                all_value_max = max(c_rec.max_value, all_value_max)
                all_value_min = min(c_rec.min_value, all_value_min)
                all_value_sum += c_rec.value
            tmp_line_formating_dict['pad_field_size'] = tmp_pad_size

        tmp_hf_dict = dict(
            default_min=self.def_counter_kwargs['min_counter'],
            default_max=self.def_counter_kwargs['max_counter'],
            num_counters=len(counters),
            value_sum=all_value_sum,
            value_min=all_value_min,
            value_max=all_value_max,
        )

        if line_indent is None:
            if header or footer:
                line_indent = 4
            else:
                line_indent = 0

        if line_format is not None and 'indent' in line_format:
            indent = ''.rjust(line_indent, ' ')
            tmp_line_formating_dict['indent'] = indent
        else:
            tmp_line_formating_dict['line_indent'] = line_indent

        tmp_lines = []
        for c in counters:
            c_rec = self.counters[c]
            tmp_hf_dict[c] = c_rec

            tmp_lines.append(c_rec.format(line_format, **tmp_line_formating_dict))

        tmp_lines = '\n'.join(tmp_lines)

        tmp_hf_dict.update(kwargs)

        tmp_ret = []
        if header:
            if '{' in header:
                tmp_ret.append(header.format(**tmp_hf_dict))
            else:
                tmp_ret.append(header)
        tmp_ret.append(tmp_lines)
        if footer:
            if '{' in footer:
                tmp_ret.append(footer.format(**tmp_hf_dict))
            else:
                tmp_ret.append(footer)

        return '\n'.join(tmp_ret)

    def keys(self):
        return self.counters.keys()

    def records(self):
        return self.counters.values()

    def values(self):
        for c in self.counters.values():
            yield int(c)

    def __iter__(self):
        for item in self.counters.values():
            yield item

    def __call__(self, key, **kwargs):
        return self.get(key)(**kwargs)

    def __contains__(self, item):
        return item in self.counters

    def __getitem__(self, item):
        return self.get(item)

    def __getattr__(self, item):
        try:
            return self.get(item)
        except KeyError:
            raise AttributeError('%s not an attribute' % item)

    def __len__(self):
        return len(self.counters)

    def dump(self, sep='\n'):
        tmp_ret = []
        for x in self.counters.values():
            tmp_ret.append(repr(x))

        if sep is None:
            return tmp_ret
        else:
            return sep.join(tmp_ret)

    def __repr__(self):
        return 'CounterSet: %s objects' % len(self)

    def __bool__(self):
        return bool(self.counters)