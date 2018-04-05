class ModelDoesNotExist(Exception):
    def __init__(self, message, model):
        super().__init__(message)
        self.model = model
