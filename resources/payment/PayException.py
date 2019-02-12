class AlipayException(Exception):

    def __init__(self, msg=None):
        super(AlipayException, self).__init__()


class AliPayValidationException(Exception):
    def __init__(self, msg=None):
        super(AliPayValidationException, self).__init__()
