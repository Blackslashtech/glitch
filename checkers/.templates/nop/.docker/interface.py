from checkeradapter import BaseCheckerAdapter, Flag, Status


class Checker(BaseCheckerAdapter):
    handler = None

    def __init__(self, host):
        super().__init__(host)

    def check(self) -> (Status):
        status = Status()
        return status

    def put(self, flag: Flag) -> (Status, Flag):
       status = Status()
       return (status, flag)

    def get(self, flag: Flag) -> (Status):
        status = Status()
        return (status, flag)
