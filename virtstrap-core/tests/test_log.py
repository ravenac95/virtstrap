"""
Test Log
--------

"""
import fudge
from nose.tools import raises
from virtstrap.testing import *
from virtstrap.log import *

def test_initialize_logger():
    logger = VirtstrapLogger()

class TestVirtstrapLogger(object):
    def setup(self):
        self.logger = VirtstrapLogger()
        self.fake_handler = fudge.Fake()

    def setup_handler(self):
        self.logger.add_handler(self.fake_handler)

    @fudge.test
    def test_logger_logs(self):
        self.setup_handler()
        fake_handler = self.fake_handler
        (fake_handler.expects('log')
            .with_args('debug', 'debugmsg\n')
            .next_call()
            .with_args('error', 'errormsg\n')
            .next_call()
            .with_args('info', 'infomsg\n')
            .next_call()
            .with_args('warning', 'warningmsg\n')
            .next_call()
            .with_args('critical', 'criticalmsg\n')
            .next_call()
            .with_args('info', 'nonewline')
        )
        logger = self.logger

        logger.debug('debugmsg')
        logger.error('errormsg')
        logger.info('infomsg')
        logger.warning('warningmsg')
        logger.critical('criticalmsg')
        logger.info('nonewline', new_line=False)

    @fudge.patch('virtstrap.log.traceback.format_exception')
    def test_logger_logs_exception(self, fake_format):
        self.setup_handler()
        fake_handler = self.fake_handler
        (fake_handler.expects('log')
            .with_args('error', 'excmsg\nsomeexception\n\n')
            .next_call()
            .with_args('debug', 'debugexcmsg\nsomeexception\n\n')
        )
        fake_format.expects_call().returns(['someexception\n'])

        logger = self.logger
        try:
            raise Exception('Exception')
        except:
            logger.exception('excmsg')
        
        try:
            raise Exception('Exception2')
        except:
            logger.debug_exception('debugexcmsg')

    @fudge.test
    def test_logger_stores_logs_before_handlers(self):
        """Logger should store logs by line in a list until a handler is set"""
        fake_handler = self.fake_handler
        (fake_handler.expects('log')
            .with_args('debug', 'debugmsg\n')
            .next_call()
            .with_args('error', 'errormsg\n')
        )
        logger = self.logger
        logger.debug('debugmsg')
        logger.error('errormsg')
        self.setup_handler()

@raises(NotImplementedError)
def test_initialize_handler():
    handler = VirtstrapLogHandler()
    handler.log('debug', 'message')

class TestVirtstrapLogHandler(object):
    def setup(self):
        ShuntLogHandler = shunt_class(VirtstrapLogHandler)
        self.handler = ShuntLogHandler()
        
    def test_handler_set_level(self):
        handler = self.handler
        (handler.__patch_method__('emit').with_args('info', 'msg')
                .next_call()
                .with_args('error', 'errormsg'))
        handler.set_level('info')
        handler.log('info', 'msg')
        handler.log('error', 'errormsg')
        handler.log('debug', 'debugmsg')

