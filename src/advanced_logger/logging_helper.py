import logging
from who_helpers.helpers import IndentHelper


class LoggingMixin(object):
    _indent = IndentHelper()
    _print_log = False
    _log = None

    @property
    def _logger(self):
        if self._log is None:
            self._log = logging.getLogger(__name__)
        return self._log

    @property
    def _log_prefix_format(self):
        return '%s'

    @property
    def _log_prefix_data(self):
        return '',

    def _call_on_log(self, lvl, msg, args):
        return lvl, msg, args

    def _log_item(self, level, msg, *args, indent=None):
        log_enabled = self._logger.isEnabledFor(level)

        if not log_enabled and not self._print_log:
            return

        if '\n' in msg:
            if args:
                msg = msg % args
            msg = msg.splitlines(keepends=False)
            for m in msg:
                self._log_item(level, m, indent=indent)
            return

        msg = self._log_prefix_format + '%s' + msg

        if indent is None:
            indent = str(self._indent)
        else:
            indent = ''.rjust(indent, ' ')

        args = self._log_prefix_data + (indent,) + args
        level, msg, args = self._call_on_log(level, msg, args)

        if self._print_log:
            if args:
                msg = msg % args
            args = []
            print('%s | %s' % (logging.getLevelName(level), msg))

        if log_enabled:
            if level == 'exception':
                self._logger.exception(msg, *args)
            else:
                self._logger.log(level, msg, *args)

    def _exception(self, *args, **kwargs):
        self._log_item(logging.ERROR, *args, **kwargs)

    def _critical(self, *args, **kwargs):
        self._log_item(logging.CRITICAL, *args, **kwargs)

    def _error(self, *args, **kwargs):
        self._log_item(logging.ERROR, *args, **kwargs)

    def _warning(self, *args, **kwargs):
        self._log_item(logging.WARNING, *args, **kwargs)

    def _debug(self, *args, **kwargs):
        self._log_item(logging.DEBUG, *args, **kwargs)

    def _info(self, *args, **kwargs):
        self._log_item(logging.INFO, *args, **kwargs)


class LoggingRecordMixin(object):
    _log_recs = None
    _record_logs = False

    def __init__(self, *args, **kwargs):
        self._log_recs = []
        super(LoggingRecordMixin, self).__init__(*args, **kwargs)

    def _call_on_log(self, lvl, msg, args):
        if self._record_logs:
            if args:
                msg = msg % args
            args = []
            self._log_recs.append('%s | %s' % (logging.getLevelName(lvl), msg))
        return lvl, msg, args

    def _log_merge_records(self, other, save_before=False):
        if self._log_recs is None:
            self._log_recs = []
        if other is not None and other._log_recs:
            other = other._log_recs

            if save_before:
                self._log_recs = other + self._log_recs
            else:
                self._log_recs.extend(other)

    def _get_logs(self, sep='\n'):
        log_recs = self._log_recs or ['Empty Logs']
        if sep is not None:
            return sep.join(log_recs)
        return log_recs

    def _clear_logs(self):
        if self._log_recs is not None:
            self._log_recs.clear()


class LoggingModelMixin(LoggingMixin):
    _model_name = None

    @classmethod
    def _get_model_name(cls):
        if cls._model_name is None:
            cls._model_name = cls.__class__.__name__
        return cls._model_name

    @property
    def _log_prefix_format(self):
        return '[%s PK: %s] '

    @property
    def _log_prefix_data(self):
        return self._get_model_name(), self.pk

    @property
    def _logger(self):
        if self._log is None:
            if hasattr(self, 'filter'):
                self._log = self.model._log
            if self._log is None:
                self._log = logging.getLogger(self._get_model_name())

        return self._log
