import sys
import threading
import logging

PY_35 = sys.version_info >= (3, 5)

class SpanBuffer(object):
    """ Buffer is an interface for storing the current active span. """

    def set(self, span):
        raise NotImplementedError()

    def get(self):
        raise NotImplementedError()


class ThreadLocalSpanBuffer(SpanBuffer):
    """ ThreadLocalSpanBuffer stores the current active span in thread-local
        storage.
    """

    def __init__(self):
        self._locals = threading.local()

    def set(self, span):
        self._locals.span = span

    def get(self):
        return getattr(self._locals, 'span', None)

    def pop(self):
        span = self.get()
        self.set(None)
        return span

if PY_35:
    import asyncio

    class TaskLocalSpanBuffer(SpanBuffer):
        """ TaskLocalSpanBuffer stores the current active span on the active asyncio Task.
        """

        PROP_NAME = '__datadog_active_span'

        def __init__(self):
            logger = logging.getLogger(__name__)
            logger.info('creating TaskLocalSpanBuffer')

        def set(self, span):
            current_task = asyncio.Task.current_task()

            setattr(current_task, TaskLocalSpanBuffer.PROP_NAME, span)

        def get(self):
            current_task = asyncio.Task.current_task()

            return getattr(current_task, TaskLocalSpanBuffer.PROP_NAME, None)

        def pop(self):
            span = self.get()
            self.set(None)
            return span
