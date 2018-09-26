import time
import datetime

class log_c:
    def __init__(self):
        self.file = ''

    def set_file(self, f_name):
        self.file = f_name

    def log(self, msg):
        print(msg)
        f = open(self.file, 'a')
        f.write('\n' + str(datetime.datetime.fromtimestamp(time.time())) + ' | ' + msg)
        f.close()
