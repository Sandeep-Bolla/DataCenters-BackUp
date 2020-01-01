import sys
from PySide2 import QtCore
from PySide2.QtWidgets import QApplication, QMainWindow, QPushButton, QMessageBox, QLabel
import Hung3 as CLI
file_name = ""

import socket
import subprocess

full_dc_id = str(socket.gethostname())
dc_id = full_dc_id[2:]


class color:
   PURPLE = '\033[95m'
   CYAN = '\033[96m'
   DARKCYAN = '\033[36m'
   BLUE = '\033[94m'
   GREEN = '\033[92m'
   YELLOW = '\033[93m'
   RED = '\033[91m'
   BOLD = '\033[1m'
   UNDERLINE = '\033[4m'
   END = '\033[0m'

class MainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.setAcceptDrops(True)
        self.setWindowTitle("LETZ BACK-UP")
        self.setGeometry(150, 100, 500, 300)
        self.printedText("Drag & Drop",100)
        self.show()


    def printedText(self,text, col):
        txt = QLabel(self)
        txt.setText(text)
        txt.move(200,col)
        txt.show()
    def send(self):
        btn = QPushButton("SEND", self)
        #btn.clicked.connect(QtCore.QCoreApplication.instance().quit)
        btn.resize(100,30)
        btn.move(200,100)
        btn.clicked.connect(self.sending_data)
        btn.show()
    def dragEnterEvent(self, e):
        if e.mimeData().hasUrls():
            e.acceptProposedAction()
    def dropEvent(self, e):
        global file_name
        for url in e.mimeData().urls():
            file_name = url.toLocalFile()
            print("Dropped file: " + file_name)
            self.send()

    def sending_data(self):
        print("Button clicked...")
        print(file_name)
        (out, err)= run_cmd(['hadoop', 'fs', '-put', str(file_name), '/myFiles'])
        print(err)
        print(out)
        print("HDFS COPY DONE")
        self.printedText("COPY DONE",150)
        self.netConf()

    def netConf(self):
        netinfo = "Network Information will be diplayed here"
        print(netinfo)
        info = QMessageBox.information(self, 'Network Info', netinfo,QMessageBox.Ok)

        if(info==QMessageBox.Ok):
            CLI.main()
            self.backup_dc_id = CLI.backup_dc_id
            print(color.BOLD +"The BackUp DC for the "+full_dc_id+" is dc"+str(self.backup_dc_id)+color.END,'\n\n')
            print('\t\t', end=' ')
            for i in range(len(file_name)-1, -1, -1):
                if file_name[i]=="/":
                    name_only = file_name[i+1:]
                    break

            (out,err)=run_cmd(['hadoop', 'distcp', 'hdfs://dc'+dc_id+':9000/myFiles/'+name_only, 'hdfs://dc'+str(self.backup_dc_id)+':9000/backupFiles/'])
            print(err)
            print(out)
            self.printedText("BACKUP DONE"+str(self.backup_dc_id) ,200)



#ToRunLinuxCommands
def run_cmd(args_list):
    """
    To Run Linux Commands
    """
    print('Running system command: {0}'.format(' '.join(args_list)))
    proc = subprocess.Popen(args_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (s_output, s_err) = proc.communicate()
    s_return = proc.returncode
    return s_output, s_err

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    #window.show()
    #app.exec_()
    sys.exit(app.exec_())
