



CONFIG_OPTIONS = dict(
    obj_formatters = None,
    allow_multiline_logging = True,
    default_indent_size = 4,
    default_object_decoder = OBJ_FORMAT_REPR,
    json_decoder = None,
    json_kwargs = None,
    use_global_timers = False,
    use_global_capture = False,
    use_global_prefix = False,
    use_global_indent = False,
)

class GlobalConfig(object):
    obj_formatters = None
    allow_multiline_logging = True
    default_indent_size = 4
    default_object_formatter = 'xxx'
    json_decoder = None
    json_kwargs = None
    use_global_timers = False
    use_global_capture = False
    use_global_prefix = False
    use_global_indent = False

    def __init__(self, formatters=None, **kwargs):
        self.set_options(CONFIG_OPTIONS)
        self.set_options(kwargs)
        self.formatters = {}
        if formatters:
            for f in formatters:
                self.add_formatter(f)

    def set_options(self, config_options):
        for f, v in config_options.items():
            if f in CONFIG_OPTIONS:
                setattr(self, f, v)

    def add_formatter(self, formatter, key=None):
        if key is None:
            key = formatter.key
        self.formatters[key] = formatter

    def get_formatter(self, key):
        return self.formatters.get(key, self.formatters[self.default_object_formatter])

