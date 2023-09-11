def exploit():
    x = 1
    for i in range(1, 1000):
        x *= i
    return x


if __name__ == '__main__':
    print(exploit())


