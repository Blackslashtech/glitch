from checkerclient import RemoteChecker, Status, StatusCode, Flag

service_id = 1
checker = RemoteChecker('localhost')
status = checker.check('localhost')
print(status)
flag = Flag('localhost', 'flag', 'flag_id')
status, flag = checker.put(flag)
print(status, flag)
status, flag = checker.get(flag)
print(status, flag)