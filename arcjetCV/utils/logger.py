class Logger(object):
    def __init__(self,filename,PRINT=True,FILEIO=False,prefix=''):
        self.filename=filename
        self.prefix = prefix
        self.print = PRINT
        self.fileio = FILEIO

    def write(self,line):
        if self.print:
            print(self.prefix+line.__str__())
        if self.fileio:
            fh = open(self.filename,'a')
            fh.write(self.prefix+line.__str__()+'\n')
            fh.close()
