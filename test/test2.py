from multiprocessing import Process, freeze_support, set_start_method

def foo():
    print('hello')

def bar():
    freeze_support()
    set_start_method('spawn')
    p = Process(target=foo)
    p.start()

print('bbb')

if __name__ == '__main__':
    bar()