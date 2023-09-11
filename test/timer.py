import subprocess
import time
import xmlrpc.client



def test_local():
    start_time = time.time()
    for i in range(1000):
        out = subprocess.check_output(['python3', 'local.py'])
    # print(out)
    end_time = time.time()
    print(f'Local execution time: {end_time - start_time}')


def test_remote():
    start_time = time.time()
    server = xmlrpc.client.ServerProxy("http://localhost:5001/")
    for i in range(1000):
        out = server.exploit()
    # print(out)
    end_time = time.time()
    print(f'Remote execution time: {end_time - start_time}')



test_local()
test_remote()