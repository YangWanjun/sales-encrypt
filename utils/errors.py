class CustomException(Exception):

    def __init__(self, message="", data=None):
        super(CustomException, self).__init__(self, message)
        self.message = message
        self.data = data
