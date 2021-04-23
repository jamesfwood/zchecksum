import sys, os
from pathlib import Path

from datetime import datetime

from winrt.windows.ui.notifications import ToastNotificationManager, ToastNotification, ToastTemplateType

from PySide6.QtWidgets import QApplication, QMainWindow, QTreeWidgetItem, QAbstractItemView, QPushButton, QStyle, QTreeWidgetItemIterator
from PySide6.QtCore import QFile, SIGNAL, QProcess
from PySide6 import QtCore
from PySide6.QtGui import QStandardItemModel, QStandardItem
from ui_MainWindow import Ui_MainWindow

from dirs import getBaseDirs
from ChecksumSet import ChecksumSet

from Sha512 import Sha512

#TODO:  Update UI file to say "Untracked/New Sets"

class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        #self.ui = ()
        self.setupUi(self)

        self.p : QProcess = None
        
        dirname = r"K:\Media Library\TV"

        processing_dirs = getBaseDirs(dirname)

        s : QtCore.QSize = self.treeView.iconSize()
        self.message(f'size = {s}')
        s = QtCore.QSize(16, 16)  # Set icon sizing here
        self.treeView.setIconSize(s)
        
        style = QApplication.style()
        self.running_icon = style.standardIcon(QStyle.SP_BrowserReload)
        self.done_icon = style.standardIcon(QStyle.SP_DialogApplyButton)
        self.failed_icon = style.standardIcon(QStyle.SP_MessageBoxCritical)

        self.checksum_sets = []

        for dirname in processing_dirs:
            self.checksum_sets.append(ChecksumSet(dirname))

        self.updateStats()

        self.populateModel()
        self.treeView.setModel(self.model)
     #   self.treeView.setExpandsOnDoubleClick(True)

  #      for x in self.iterItems(self.model.invisibleRootItem()):
        #    y = x.data(role=DisplayRole)
       #     z = x.data(role=UserRole)
        #    self.message(f'y = {y}, z = {z}')
        #    x.setText('hi')
   #         y = x.data(role=QtCore.Qt.UserRole)
    #        self.message(x.text())
            
    #        self.message('HI' + y.baseDirname)
    #        self.message('HI' + str(y))


        self.start_process()

     #   model.setHorizontalHeaderLabels(['Title', 'Summary'])
     #   rootItem = model.invisibleRootItem()

        #First top-level row and children 
     #   item0 = [QStandardItem('Title0'), QStandardItem('Summary0')]
    #    item00 = [QStandardItem('Title00'), QStandardItem('Summary00')]
    #    item01 = [QStandardItem('Title01'), QStandardItem('Summary01')]
     #   rootItem.appendRow(item0)
    #    item0[0].appendRow(item00)
    #    item0[0].appendRow(item01)

        #Second top-level item and its children
    #    item1 = [QStandardItem('Title1'), QStandardItem('Summary1')]
    #    item10 = [QStandardItem('Title10'), QStandardItem('Summary10')]
    #    item11 = [QStandardItem('Title11'), QStandardItem('Summary11')]
    #    item12 = [QStandardItem('Title12'), QStandardItem('Summary12')]
    #    rootItem.appendRow(item1)
    #    item1[0].appendRow(item10)
    #    item1[0].appendRow(item11)
    #    item1[0].appendRow(item12)

        #Children of item11 (third level items)
    #    item110 = [QStandardItem('Title110'), QStandardItem('Summary110')]
    #    item111 = [QStandardItem('Title111'), QStandardItem('Summary111')]
    #    item11[0].appendRow(item110)
    #    item11[0].appendRow(item111)


    def toast_notification(self, title, text):
        AppID = 'zchecksum'
        XML = ToastNotificationManager.get_template_content(ToastTemplateType.TOAST_TEXT02)
        print(XML)
        t = XML.get_elements_by_tag_name("text")
        print(t)
        t[0].append_child(XML.create_text_node(title))
        t[1].append_child(XML.create_text_node(text))
        notifier = ToastNotificationManager.create_toast_notifier(AppID)
        notifier.show(ToastNotification(XML))
        

    def iterItems(self, root):
        if root is not None:
            for row in range(root.rowCount()):
                row_item = root.child(row, 0)
                if row_item.hasChildren():
                    for childIndex in range(row_item.rowCount()):
                        # Take second column from "child"-row
                        child = row_item.child(childIndex, 1)
                        yield child


    def populateModel(self):

        self.model = QStandardItemModel()
        self.model.setHorizontalHeaderLabels(['Status', 'Directory / Filename', 'File Count', 'Size (MB)', 'Checksum', 'Last Verified'])
        rootItem = self.model.invisibleRootItem()

        for checksum_set in self.checksum_sets:
            last_verified = ''
            status = ''
            if not checksum_set.hasSha512File():
                status = 'New'
            elif checksum_set.has_changes():
                status = "Modified"
                self.toast_notification("Modified Set", checksum_set.baseDirname)
            else:
                time_delta = datetime.now() - checksum_set.sha512File.last_verified
                last_verified = f'{time_delta.days} days ago'
                if time_delta.days > 30:
                    status = 'Test'
                else:
                    status = 'Good'

            if status is 'Test' or status is 'New':
                item = [QStandardItem(status), QStandardItem(checksum_set.baseDirname), QStandardItem(str(len(checksum_set.filenames))), QStandardItem(''), QStandardItem(''), QStandardItem(last_verified)]
                for filename in checksum_set.filenames:
                    checksum_text = ''
                    if checksum_set.sha512File:
                        checksum = checksum_set.sha512File.findChecksum(filename)
                        if checksum:
                            checksum_text = checksum
                    size = Path(checksum_set.baseDirname + filename).stat().st_size
                    size_mb = size / 1024 / 1024
                    c_item = [QStandardItem(''), QStandardItem(filename), QStandardItem(''), QStandardItem(f'{size_mb:.1f} MB'), QStandardItem(checksum_text)]
                    c_item[1].setData(checksum_set, QtCore.Qt.UserRole)
                    item[0].appendRow(c_item)
                rootItem.appendRow(item)




     #   self.start_process()

     #   header = self.treeWidget.header()
      #  header
    #    header.setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)
    #    header.setStretchLastSection(False)
     #   header.setSectionResizeMode(5, QtWidgets.QHeaderView.Stretch)


    def updateStats(self):
        new_count = 0
        modified_count = 0
        test_count = 0
        good_count = 0

    #    items = []
        for checksum_set in self.checksum_sets:
            if not checksum_set.hasSha512File():
                new_count += 1
            elif checksum_set.has_changes():
                modified_count += 1
            else:
                time_delta = datetime.now() - checksum_set.sha512File.last_verified
                if time_delta.days > 30:
                    test_count += 1
                else:
                    good_count += 1

        self.statusBar().showMessage(f'Total sets: {len(self.checksum_sets)} sets.   New sets: {new_count}   Modified sets: {modified_count}   Test sets: {test_count}   Good sets: {good_count}')


    def message(self, s):
    #    self.statusBar().showMessage(s)
        self.listWidget.addItem(s)


    def start_process(self):
        root = self.model.invisibleRootItem()

        started_count = 0

        if root is not None:
            for row in range(root.rowCount()):

                if self.p:
                    break

                row_item = root.child(row, 0)
              #  item = self.model.item(row)
                dir = root.child(row, 1)
                set_status = root.child(row, 0)

         #       self.message(dir.text())
                if (set_status.text() == "New" or set_status.text() == 'Test') and row_item.hasChildren():
                    for childIndex in range(row_item.rowCount()):
                        # Take second column from "child"-row
                      #  status = row_item.child(childIndex, 0)

                     #   self.message(status.text())
              #          if status.text() == 'New':
              #              self.message(dir.text())

                        status = row_item.child(childIndex, 0)
                        filename = row_item.child(childIndex, 1)
                  #      self.message(filename.text())
                     #   checksum_item = row_item.child(childIndex, 4)
                    
                        if status.text() != "Done":
                      #      parent = filename.parent()
                     #       self.message("parent " + str(parent))
                            
                            self.run_process(dir.text(), filename.text(), row_item, childIndex)
                            started_count += 1


                            if self.p:
                                break
        
        self.message(f'start_process done.  Started {started_count}')

                      #  yield child

   #     for i in range(self.model.rowCount()):
   #                 item = self.model.item(i)

    #    root = self.treeWidget.invisibleRootItem()
    #    child_count = root.childCount()
    #    for i in range(child_count):
    #        item = ro
    # ot.child(i)
     #       url = item.text(0) # text at first (0) column
    #        item.setText(1, 'result from %s' % url) # update result column (1)
        

    def run_process(self, dir, filename, set_item, childIndex):
        if self.p is None:  # No process running.
            self.p_item = dict(set_item=set_item, child_index=childIndex )
            self.p = QProcess()  # Keep a reference to the QProcess (e.g. on self) while it's running.
     
        #    item
     #       self.p.readyReadStandardOutput.connect(self.handle_stdout)
            self.p.readyReadStandardError.connect(self.handle_stderr)
            self.p.stateChanged.connect(self.handle_state)
            self.p.finished.connect(self.process_finished)  # Clean up once complete.

         #   filename = r"J:\Media Library\TV\New\Family Guy\Misc\Family Guy S07E11.avi"

            filepath = dir + filename
            self.message("Executing process for file: " + filepath)

            args = ["-hashfile", filepath, "SHA512"]
            self.p.start("certutil", args)

            status = set_item.child(childIndex, 0)

            status.setIcon(self.running_icon)
            set_item.setIcon(self.running_icon)

            if status.text() == '':
                if set_item.text() != 'Test':
                    set_item.child(childIndex, 0).setText('Running Pass 1/3')
                else:
                    set_item.child(childIndex, 0).setText('Running')
            elif status.text() == 'Running Pass 1/3':
                set_item.child(childIndex, 0).setText('Running Pass 2/3')
            elif status.text() == 'Running Pass 2/3':
                set_item.child(childIndex, 0).setText('Running Pass 3/3')

        else:
            self.message("process already running!")




    def handle_stderr(self):
        data = self.p.readAllStandardError()
        stderr = bytes(data).decode("utf8")
        # Extract progress if it is in the data.
   #     progress = simple_percent_parser(stderr)
   #     if progress:
   #         self.progress.setValue(progress)
        self.message(stderr)

    def handle_stdout(self):
        data = self.p.readAllStandardOutput()
        stdout = bytes(data).decode("utf8")
        self.message(stdout)

    def handle_state(self, state):
        states = {   
            QProcess.NotRunning: 'Not running',
            QProcess.Starting: 'Starting',
            QProcess.Running: 'Running',
        }
        state_name = states[state]
        self.message(f"State changed: {state_name}")


    def process_finished(self, exitCode, exitStatus):

        row_item = self.p_item['set_item']
        child_index = self.p_item['child_index']
        status_item = row_item.child(child_index, 0)
        filename_item = row_item.child(child_index, 1)

        try:
            checksum_set = filename_item.data(QtCore.Qt.UserRole)

            if checksum_set is None:
                self.toast_notification("Checksum Set Not Found", "No checksum set for file " + filename_item.text())
                raise Exception("No checksum set found")

            self.message(f'Process finished. exitCode = {exitCode}, exitStatus = {exitStatus}, baseDirname = {checksum_set.baseDirname}')

            data = self.p.readAllStandardOutput()

     #       stdout = bytes(data)
      #      self.message("normal stdout: " + stdout)
    #  .decode('iso-8859-1').encode('utf8')
        #    stdout = bytes(data).decode("iso-8859-1")
            #try:
            stdout = bytes(data).decode('utf8', 'replace')
          #  except:
          #      stdout = bytes(data).decode('iso-8859-1')


        #   self.message("row_item" + row_item)
            self.message("stdout: " + stdout)
            
            lines = stdout.splitlines()

            if exitCode != 0 or len(lines) != 3:
                msg = f'Error: Compute SHA512 failed.  stdout: ({stdout})'
             #   msg = f'Error: Compute SHA512 failed for file {filename}.  stdout: ({cp.stdout}) stderr: ({cp.stderr})'
        #       print(msg)
                self.toast_notification('Failed Compute Checksum', filename_item.text())
                raise Exception(msg)

            new_checksum = lines[1].replace(" ", "")

            checksum_item = row_item.child(child_index, 4)

            old_checksum = checksum_item.text()

            if old_checksum == "":
                checksum_item.setText(new_checksum)
            elif new_checksum != old_checksum:
                    msg = f'Error: Checksums do not match.'
                    self.toast_notification('Failed Checksum Test', filename_item.text())
                    raise Exception(msg)

            if status_item.text() == "Running Pass 3/3" or status_item.text() == 'Running':
                status_item.setText('Done')
                status_item.setIcon(self.done_icon)

        #   checksum = QStandardItem()
        #   row_item.setChild(0, 4, checksum)
        # my_item.setText()

        #  my_item.setText(0, "Done")
        #  self.message("my_item: " + my_item.text(1))

    #     if self.all_files_done_checksum(row_item.parent()):
        #        self.create_sha_file(my_item.parent())
        
            if self.all_files_done_checksum(row_item):
                row_item.setIcon(self.done_icon)
                row_item.setText("Done")
                if checksum_set.hasSha512File():
                    self.message(f'Updating {checksum_set.baseDirname} checksum file modified date')
                    checksum_set.update_modified()
                else:
                    self.create_sha_file(row_item)
        except Exception as e:
            status_item.setText("Failed")
            status_item.setIcon(self.failed_icon)
            row_item.setText("Failed")
            row_item.setIcon(self.failed_icon)
            self.message("ERROR: " + str(e))
        finally:
            self.p = None   
            self.start_process()


    def all_files_done_checksum(self, set_item):
        for childIndex in range(set_item.rowCount()):
            status_item = set_item.child(childIndex, 0)
            checksum_item = set_item.child(childIndex, 4)
            filename_item = set_item.child(childIndex, 1)
            self.message(filename_item.text())

            if status_item.text() != 'Done' or checksum_item.text() == '':
                return False
        
        return True


    def create_sha_file(self, set_item):
        self.message("create_sha_file!!")

       # index = set_item.index()

      #  self.message(f'index = {index}')
      #  dirname = self.model.item(index, 1)

     #   dirname = set_item.data(1)  
       
        dir = self.model.invisibleRootItem().child(set_item.row(), 1)

        dirname = dir.text()
        self.message(f'create_sha_file2, dir = {dir.text()}, row = {set_item.row()}, set_item.columnCount = {set_item.columnCount()}')

        shaFile = Sha512(dirname)

        for childIndex in range(set_item.rowCount()):
            checksum_item = set_item.child(childIndex, 4)

            filename_item = set_item.child(childIndex, 1)
            self.message(filename_item.text())

            shaFile.addFileAndChecksum(filename_item.text(), checksum_item.text())

        shaFile.writeFile()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec_())

