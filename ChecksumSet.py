import os
from datetime import datetime
import subprocess
from pathlib import Path

from Sha512 import Sha512
#from win10toast import ToastNotifier
#toaster = ToastNotifier()

class ChecksumSet:

    def __init__(self, dirname):
        self.baseDirname = dirname
        self.filenames = []
        self.sha512File = None

        if not self.baseDirname.endswith("\\"):
            self.baseDirname += "\\"

    #    print(f'\nLoading dir: {self.baseDirname}')

        # r=root, d=directories, f=files
        for r, d, f in os.walk(self.baseDirname):
            for filename in f:
                
                # All filenames are relative to baseDirname
                filename = os.path.join(r, filename).replace(self.baseDirname, "")

                if os.path.basename(filename) == "zchecksum.sha512":
     #               print(f'Found {filename} file.  Loading...  sha512file = {self.sha512File}')
                    self.loadSha512(filename)
                else:
                    self.filenames.append(filename)
    #                print(f'Found file = {filename}')

        if self.sha512File:
        
            if self.has_changes():
                print(f"Set '{self.baseDirname[:-1]}' has changes (will skip...):")
                self.print_missing_from_dir()
                self.print_missing_from_sha512()
     #       else:
     #           time_delta = datetime.now() - self.sha512File.last_verified
      #          if time_delta.days > 1:
     #               print(f"Verifying Set '{self.baseDirname[:-1]}' (Last verified {time_delta.days} ago).")
 
###       else:
###            print(f"Set '{self.baseDirname[:-1]}' is *NEW* with {len(self.filenames)} files:")
###            for f in self.filenames:
###                print(f'     + {f}')

     #   print(f'Set {self.baseDirname} has {len(self.filenames)} files.')

        # This dir does not have a SHA512SUMS.txt file, need to build it
    #    if self.sha512File is None:
    #        self.createNewShaFile()


    def update_modified(self):
        if self.sha512File:
            self.sha512File.update_modified()


    def print_verify(self, days_to_verify):
        if self.sha512File and not self.has_changes():
            time_delta = datetime.now() - self.sha512File.last_verified
            if time_delta.days > days_to_verify:
                print(f"     {os.path.basename(self.baseDirname[:-1])}  (Last verified {time_delta.days} days ago)")
    

    def print_missing_from_dir(self):
        if self.sha512File is None:
            msg = "ERROR: Must have a sha512 file for print_missing_from_dir!"
            print(msg)
            raise Exception(msg)

        for n in self.sha512File.file_list:
            filename = n['filename']
            if filename not in self.filenames:
                print(f"     - {filename}")


    # check if any files in dir are missing from the sha512 file
    def print_missing_from_sha512(self):
        for f in self.filenames:
            found = False
            for n in self.sha512File.file_list:
                filename = n['filename']
                if f == filename:
                    found = True
                    break
            if not found:
                print(f'     + {f}')


    def has_changes(self):
        missing_files = self.any_missing_from_dir(silent=True)
        added_files = self.any_added_to_dir(silent=True)

        return missing_files or added_files


    # check if any files in sha512 file are missing from directory
    def any_missing_from_dir(self, silent=False):
        if self.sha512File is None:
            msg = "ERROR: Must have a sha512 file for any_missing_from_dir!"
            print(msg)
            raise Exception(msg)

        for n in self.sha512File.file_list:
            filename = n['filename']
            if filename not in self.filenames:
                if not silent:
                    msg = f'Error: Set {self.baseDirname} is missing file {filename} in dir from SHA512 checksum\n\n'
           #         toaster.show_toast("zchecksum", msg)
                    print(msg)

                # TODO: put in Windows Toaster Notify
                return True

        return False

    # get list of files in sha512 file are missing from directory
    def get_missing_from_dir(self):
        missing_list = []
        if self.sha512File is None:
            msg = "ERROR: Must have a sha512 file for get_missing_from_dir!"
            print(msg)
            raise Exception(msg)

        for n in self.sha512File.file_list:
            filename = n['filename']
            if filename not in self.filenames:

                missing_list.append(filename)

        return missing_list

    # check if any files in dir and not in sha512 file
    def any_added_to_dir(self, silent=False):
        for f in self.filenames:
            found = False
            for n in self.sha512File.file_list:
                filename = n['filename']
                if f == filename:
                    found = True
                    break
            if not found:
                if not silent:
                    msg = f'     * Missing file {f} in SHA512 checksum file.'
         #           toaster.show_toast("zchecksum", msg)
                    print(msg)
                return True
        
        return False


    def compare(self, newSha512):

        if self.sha512File is None:
            msg = "ERROR: Must have a sha512 file for compare!"
            print(msg)
            raise Exception(msg)

        for n in newSha512.file_list:

            filename = n['filename']
            checksum = self.sha512File.findChecksum(filename)

            if checksum is None:
                print(f'Warning: {filename} not found in checksum file.  Adding file...')
                # TODO: report to Windows 10 Toaster notification
        #        return False
                
            if n['checksum'] != checksum:
                print(f'Checksum for {filename} does not match.  Match failed!')
                # TODO: report to Windows 10 Toaster notification
                return False
        
        return True


    def print(self):

        print(f'ChecksumSet: {self.baseDirname}')

        for f in self.filenames:
            print(f)
        
        if self.sha512File:
            print("**** Found SHA512 file ****\n")
        else:
            print("No SHA512 file found")


    def hasSha512File(self):

        return self.sha512File is not None


    def loadSha512(self, shaFilename):

        if self.sha512File is not None:
            msg = "ERROR: Should not have more than one sha512 file per checksum dir! " + self.baseDirname
            print(msg)
            raise Exception(msg)

        if 'Voyager s04e20' in self.baseDirname:
            print('im at s04e20')

        self.sha512File = Sha512(self.baseDirname, shaFilename)

    #    self.sha512File.print()


    def generateSha512(self):

    #    print(f'     Generating SHA512 checksum file:')

        sha512 = Sha512(self.baseDirname)

        for filename in self.filenames:
            checksum = self.computeSha512(filename)
            sha512.addFileAndChecksum(filename, checksum)

    #    sha512.print()

        return sha512


    def updateShaFile(self, sha512):

        self.sha512File = sha512
        self.sha512File.writeFile()


    def computeSha512(self, filename):
        print(f"     Computing SHA512 for file '{filename}'...")
 #       toaster.show_toast("zchecksum", filename)
        size = Path(self.baseDirname + filename).stat().st_size
        if size == 0:
            return "cf83e1357eefb8bdf1542850d66d8007d620e4050b5715dc83f4a921d36ce9ce47d0d13c5d85f2b0ff8318d2877eec2f63b931bd47417a81a538327af927da3e"
        
        t0 = datetime.now().replace(microsecond=0)
        cp = subprocess.run(["certutil","-hashfile", self.baseDirname + filename, "SHA512"], universal_newlines=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        t1 = datetime.now().replace(microsecond=0)
        
        tdelta = t1-t0

        if tdelta.total_seconds() > 0.0:
            mb_per_second = (size / 1024 / 1024) / tdelta.total_seconds()
            print(f'          Elapsed time: {t1-t0}    Speed: {mb_per_second:.2f} MB/s')
        else:
            print(f'          Elapsed time: {t1-t0}')

    #    print()
        
        lines = cp.stdout.splitlines()

        if cp.returncode != 0 and len(lines) != 3:
            msg = f'Error: Compute SHA512 failed for file {filename}.  stdout: ({cp.stdout}) stderr: ({cp.stderr})'
     #       print(msg)
            raise Exception(msg)


        return lines[1].replace(" ", "")
