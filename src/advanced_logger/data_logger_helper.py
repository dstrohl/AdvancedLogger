"""
This utility provides a logging process where timing data is captured and logged.  at some point it should be
merged with lps_timer with does a similar process.

"""
__author__ = 'strohl'
__version__ = '0.9'
__status__ = 'Testing'


import logging
from uuid import uuid1
from advanced_counter.helpers import get_now

__all__ = ['DataLogger']

"""
Data log specs:
data, [start], in_out, session_id, parent_session_id, parent_delta_secs, session_group, equested_url, 0, 0, 0, 0
date, [end], in_out, session_id, parent_session_id, parent_delta_secs, session_group, requested_url, response_time, response_code, response_size, retries
"""


data_log = logging.getLogger('skytap.data_log')
log = logging.getLogger('data_logger_proc')


def log_data_header():
    tmp_ret = [
        'start_time',
        'parent_child',
        'session_id',
        'request_type',
        'url',
        'method',
        'retry_numb',
        'retry_delta_sec',
        'request_data',
        'response_code',
        'response_size',
        'response_time',
        'response_text',
        'response_headers',
        'is_error',
    ]
    data_log.info(','.join(tmp_ret))

#  "log_date","start_time","parent_child","session_id","request_type","url","method","retry_numb","retry_delta_sec","request_data","response_code","response_size","response_time","response_text","response_headers","is_error"


class DataLogger(object):
    """
    request_data:
        account,
        date,
        parent_child,
        request_type,
        session_id,
        requested_url,
        requested_method
        retry_num,
        retry_delta-sec,
        request_data,
    response_data:
        response_code,
        response_size,
        response_time_sec,
        response_text,
        response_headers,
        is_error,
    """
    def __init__(self, account, url, method, request_type='Unk', data=None, parent=None, retry_num=-1, trim_to=1000):
        self.account = account
        self.url = url
        self.parent = parent
        self.method = method
        self.request_data = data
        self.retry_delta_sec = None
        self.finished = False
        self.last_child_end = None
        self.request_type = request_type
        self.trim_to = trim_to
        if parent is None:
            self.session_id = uuid1()
            self.is_parent = True
            self.retry_num = -1
        else:
            self.session_id = parent.session_id
            self.is_parent = False
            self.retry_num = retry_num
            if parent.last_child_end is None:
                self.retry_delta_sec = 0
            else:
                self.retry_delta_sec = get_now() - parent.last_child_end
                self.retry_delta_sec = self.retry_delta_sec.total_seconds()
        self.start_time = get_now()

    def make_child(self, url, method, data=None):
        return DataLogger(account=self.account, url=url, method=method, data=data, parent=self, request_type=self.request_type,
                          retry_num=self.retry_num+1)

    def quote(self, text_in):
        if not isinstance(text_in, str):
            text_in = repr(text_in)
        if text_in and text_in[0] == '"' and text_in[-1] == '"':
            text_in = text_in[1:-1]
        if '"' in text_in:
            text_in = text_in.replace('"', "'")
        if '\n' in text_in:
            text_in = text_in.replace('\n', ' - ')
        if '|' in text_in:
            text_in = text_in.replace('|', ':')

        text_in = text_in[:self.trim_to]

        return text_in

    def end(self, response_code=None, response_text=None, response_headers=None, response_size=None):
        if self.finished:
            return
        self.finished = True
        if self.parent is not None:
            self.parent.last_child_end = get_now()
        response_time = get_now() - self.start_time
        response_time = response_time.total_seconds()
        is_error = response_code != 200

        if self.is_parent:
            parent_child = 'parent'
        else:
            parent_child = 'child'

        tmp_ret_l = [
            self.quote(self.account),
            str(self.start_time),
            self.quote(parent_child),
            self.quote(str(self.session_id)),
            self.quote(self.request_type),
            self.quote(self.url),
            self.quote(self.method),
            str(self.retry_num),
            str(self.retry_delta_sec),
            self.quote(self.request_data),
            self.quote(response_code),
            str(response_size),
            self.quote(response_time),
            self.quote(response_text),
            self.quote(response_headers),
            self.quote(is_error),
        ]

        """
        tmp_ret_d = dict(
            start_time=self.start_time,
            parent_child=parent_child,
            session_id=self.session_id,
            request_type=self.request_type,
            url=self.url,
            method=self.method,
            retry_num=self.retry_num,
            retry_delta=self.retry_delta_sec,
            request_data=self.request_data,
            response_code=response_code,
            response_size=response_size,
            response_time=response_time,
            response_text=response_text,
            response_headers=response_headers,
            is_error=is_error,
        )
        """
        # data_log.info('data', extra=tmp_ret_d)

        tmp_ret_l = '|'.join(tmp_ret_l)
        data_log.info(tmp_ret_l)
        log.debug(tmp_ret_l)
        return tmp_ret_l

    def __enter__(self):
        self.start_time = get_now()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            if not self.finished:
                self.end()
        else:
            if hasattr(exc_val, 'code'):
                resp_code = exc_val.code
            elif hasattr(exc_val, 'status_code'):
                resp_code = exc_val.status_code
            else:
                try:
                    resp_code = exc_type.__name__
                except:
                    resp_code = 'Error'

            if hasattr(exc_val, 'text'):
                resp_text = exc_val.text
            else:
                resp_text = str(exc_val)
            self.end(response_code=resp_code, response_text=resp_text)
