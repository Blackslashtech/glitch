import xmlrpc.server

def exploit():
    x = 1
    for i in range(1, 1000):
        x *= i
    return str(x)


server = xmlrpc.server.SimpleXMLRPCServer(("0.0.0.0", 5001))
server.register_function(exploit, "exploit")
server.serve_forever()