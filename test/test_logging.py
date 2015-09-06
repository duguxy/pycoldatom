import logging
import zmq

class ZeroMQHandler(logging.Handler):
    def __init__(self, uri, socktype=zmq.PUB, ctx=None):
        logging.Handler.__init__(self)
        self.ctx = ctx or zmq.Context()
        self.socket = zmq.Socket(self.ctx, socktype)
        self.socket.bind(uri)

    def close(self):
        self.socket.close()

    def emit(self, record): 
        """ 
        Emit a record. 
 
        Writes the LogRecord to the queue, preparing it for pickling first. 
        """ 
        try: 
            # The format operation gets traceback text into record.exc_text 
            # (if there's exception data), and also puts the message into 
            # record.message. We can then use this to replace the original 
            # msg + args, as these might be unpickleable. We also zap the 
            # exc_info attribute, as it's no longer needed and, if not None, 
            # will typically not be pickleable. 
            self.format(record) 
            record.msg = record.message 
            record.args = None 
            record.exc_info = None 
            data = pickle.dumps(record.__dict__)
            self.socket.send(data)
        except (KeyboardInterrupt, SystemExit): 
            raise 
        except Exception: 
            self.handleError(record)

handler = ZeroMQHandler('tcp://127.0.0.1:9024')
some_logger = logging.getLogger('aaa')
some_logger.addHandler(handler)
some_logger.debug('test')