from flask import Response


class ErrorResponse(Response):
    def __init__(self, status_code, message):
        super().__init__(status=status_code)