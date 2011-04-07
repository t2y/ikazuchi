# -*- coding: utf-8 -*-

import abc

class BaseHandler(object):
    """Base class for handler"""

    __metaclass__ = abc.ABCMeta

    method_name = "translate"

    @abc.abstractmethod
    def _call_method(self, method): pass
