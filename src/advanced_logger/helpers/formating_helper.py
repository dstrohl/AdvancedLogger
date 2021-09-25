import textwrap

__all__ = ['pretty_print_output', 'pp', 'ppl']


OBJ_FORMAT_STR = 'str'
OBJ_FORMAT_REPR = 'repr'
OBJ_FORMAT_PP = 'pp'
OBJ_FORMAT_JSON = 'json'



def _pp(data_in, align_sep=True, sep=' = ', line_len=None, min_line_len=50, max_values=50, sort_keys=True,
        keys_as_sections=False, filter_none=True, sort_values=False, list_bullet='- ', repr_string=False,
        filter_empty=True, key_lookup_dict=None, recurse_level=3, line_1_prefix=''):
    tmp_ret = []
    line_prefix = ''.rjust(len(line_1_prefix), ' ')

    if line_len:
        line_len = line_len - len(line_1_prefix)
        line_len = max(line_len, min_line_len)

    if data_in is None and filter_none:
        return []

    elif isinstance(data_in, str):
        if data_in == '' and filter_empty:
            return []
        if repr_string:
            data_in = repr(data_in)
        if '\n' in data_in:
            data_in = data_in.splitlines(keepends=False)
            tmp_ret.extend(data_in)
        else:
            tmp_ret.append(data_in)
    elif isinstance(data_in, dict):
        if recurse_level <= 0:
            tmp_ret.append(repr(data_in))
        elif not data_in:
            if filter_empty:
                return []
            else:
                return [line_1_prefix + '{}']
        else:
            keys = list(data_in.keys())
            if sort_keys:
                keys.sort()
            extra_val = None
            max_key_len = 0

            if max_values and len(keys) > max_values:
                extra_val = f'[+{len(keys) - max_values} more]'

                keys = keys[:max_values]

            if align_sep and not keys_as_sections:
                if key_lookup_dict:
                    tmp_keys = []
                    for k in keys:
                        if key_lookup_dict:
                            tmp_keys.append(key_lookup_dict.get(k, k))
                        else:
                            tmp_keys.append(k)
                    max_key_len = max(map(len, tmp_keys))
                else:
                    max_key_len = max(map(len, keys))

            if extra_val:
                max_key_len = max(max_key_len, len(extra_val))

            for key in keys:
                value = data_in[key]
                tmp_sec_key = None
                if key_lookup_dict:
                    key = key_lookup_dict.get(key, key)
                if keys_as_sections:
                    tmp_sec_key = key
                    l1 = '    '
                else:
                    l1 = key.rjust(max_key_len, ' ') + sep

                value = _pp(value, align_sep=align_sep, sep=sep, line_len=line_len, min_line_len=min_line_len,
                            max_values=max_values, sort_keys=sort_keys, list_bullet=list_bullet,
                            repr_string=repr_string,
                            sort_values=sort_values, keys_as_sections=keys_as_sections, filter_none=filter_none,
                            filter_empty=filter_empty, key_lookup_dict=key_lookup_dict,
                            recurse_level=recurse_level - 1,
                            line_1_prefix=l1
                            )
                if value and tmp_sec_key:
                    tmp_ret.append(tmp_sec_key)

                tmp_ret.extend(value)
            if extra_val:
                tmp_ret.append(extra_val)

    elif hasattr(data_in, '__iter__'):
        line_count = 0
        if recurse_level <= 0:
            tmp_ret.append(repr(data_in))
        elif not data_in:
            if filter_empty:
                return []
            else:
                return [line_1_prefix + repr(data_in)]
        else:
            if sort_values:
                try:
                    data_in.sort()
                except Exception:
                    pass
            extra_val = None
            extra_count = len(data_in) - max_values
            for value in data_in:
                line_count += 1
                if max_values is not None and line_count > max_values:
                    tmp_ret.append(f'[+{extra_count} more]')
                    break
                value = _pp(value, align_sep=align_sep, sep=sep, line_len=line_len, min_line_len=min_line_len,
                            max_values=max_values, sort_keys=sort_keys, list_bullet=list_bullet,
                            repr_string=repr_string,
                            sort_values=sort_values, keys_as_sections=keys_as_sections, filter_none=filter_none,
                            filter_empty=filter_empty, key_lookup_dict=key_lookup_dict,
                            recurse_level=recurse_level - 1,
                            line_1_prefix=list_bullet,
                            )
                tmp_ret.extend(value)

    else:
        tmp_ret.append(repr(data_in))

    tmp_ret_2 = []

    for l in tmp_ret:
        if line_len:
            if len(l) > line_len and not l.endswith('[...]'):
                l = l[:line_len - 6] + ' [...]'

        if not tmp_ret_2:
            tmp_ret_2.append(line_1_prefix + l)
        else:
            tmp_ret_2.append(line_prefix + l)

    return tmp_ret_2


def pretty_print_output(data_in, header=None, footer=None, align_sep=True, sep=' = ', line_len=None,
                        min_line_len=50,
                        max_values=50, sort_keys=True, keys_as_sections=False, list_bullet='- ', repr_string=False,
                        filter_none=True, sort_values=False, filter_empty=True, key_lookup_dict=None,
                        recurse_level=3,
                        value_if_empty='No Data', indent='', ret_as_list=False, data_indent=''):

    """
    takes dict and outputs it as such:

    header foobar str

    key = value
    key = value
    key = value
          value line 2
          value line 3
    key = - list1,
          - list2,
          - list3,
    key = dict_key  =
          dict_ket2 =
          dict_key3 = blah
    line 3
    line 4
    footer foobar str

    @param data_in:
    @param header: a string header to include above the output
    @param footer: a string footer to include below the output
    @param align_sep: T/F if True, will align the separators and all values will start at the same point
    @param sep: the separators between keys and values
    @param repr_string: T/F will use "repr(obj)" for strings.
    @param line_len: the max line length allowed.
    @param min_line_len: the min line length allowed (as lines are indented, the max line length can get too short, this protects against very small lines)
    @param sort_values: the system will sort any lists of values
    @param sort_keys: the system will sort keys from a dict
    @param list_bullet: The system will pre-pend this string to any list items
    @param max_values: The max number of values to include (None = no max)
    @param keys_as_sections: T/F keys will be on a separate line, values indented below them.
    @param filter_none: T/F Should not print any None values
    @param filter_empty: T/F  should not print any empty values (no '')
    @param key_lookup_dict: a dict to use to replace keys with better strings.
    @param recurse_level: [None] how many levels to recurse before simply doing a __repr__
    @param value_if_empty: The system will return this if the value passed is empty.
    @param indent: a string that is pre-pended to each line.
    @param data_indent: a string that is pre-pended to each line of the data. (note this is additive to the indent field)
    @param ret_as_list: T/F should the system return a list of lines instead of a string.
    @return:
    """

    if not data_in:
        tmp_data = [value_if_empty]
    else:
        tmp_data = _pp(data_in,
                       align_sep=align_sep,
                       sep=sep,
                       line_len=line_len,
                       min_line_len=min_line_len,
                       max_values=max_values,
                       sort_keys=sort_keys,
                       keys_as_sections=keys_as_sections,
                       list_bullet=list_bullet,
                       filter_none=filter_none,
                       sort_values=sort_values,
                       filter_empty=filter_empty,
                       key_lookup_dict=key_lookup_dict,
                       recurse_level=recurse_level,
                       repr_string=repr_string,
                       line_1_prefix='')
    tmp_data = '\n'.join(tmp_data)
    if data_indent:
        tmp_data = textwrap.indent(tmp_data, data_indent)
    tmp_data = tmp_data.splitlines(keepends=False)

    tmp_ret = []

    if header:
        tmp_ret.append(str(header))
    if tmp_data:
        tmp_ret.extend(tmp_data)
    else:
        tmp_ret.append(value_if_empty)
    if footer:
        tmp_ret.append(str(footer))

    tmp_ret = '\n'.join(tmp_ret)
    if indent:
        tmp_ret = textwrap.indent(tmp_ret, indent)

    if ret_as_list:
        return tmp_ret.splitlines(keepends=False)
    else:
        return tmp_ret

def pph(*args, **kwargs):
    return pretty_print_output(*args, **kwargs)

def ppl(*args, **kwargs):
    kwargs['ret_as_list'] = True
    return pretty_print_output(*args, **kwargs)




class ObjFormatterBase(object):

