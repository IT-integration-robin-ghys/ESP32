import os

files = os.listdir()
if len(files) > 1:
    print('The device have %d files' % len(files))
    for i in range(len(files)):
        if files[i] != 'boot.py':
            print('file name:', files[i])
            exec(open(files[i]).read(), globals())
else:
    print("MicroPython has no files!")