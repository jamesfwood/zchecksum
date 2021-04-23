import os

def getSubDirs(dirname):

    dirnames = []

    # r=root, d=directories, f=files
    for r, d, f in os.walk(dirname):
        for filename in f:

            if r not in dirnames:
                dirnames.append(r)
    
    dirnames = dirnames[1:]

    dirnames = list(dict.fromkeys(dirnames))

#    for d in dirnames:
#        print(d)

#    print(f'subdir size = {len(dirnames)}')

    return dirnames


def getBaseDirs(dirname):


    #ignoreList = [ 'Incomplete' ]

    dirnames = []

    # r=root, d=directories, f=files
    for r, d, f in os.walk(dirname):
        for filename in f:

            print(f'filename is {filename}')
            if r not in dirnames and 'Incomplete' not in r:
                dirnames.append(r)

            # All filenames are relative to baseDirname
            #self.filenames.append(filename)

            #print(f'Found file = {r}')

            #if filename == "SHA512SUMS.txt":
             #   self.loadSha512(filename)
    
    dirnames = list(dict.fromkeys(dirnames))

 #   for d in dirnames:
 #       print(d)

 #   print(f'dirnames size = {len(dirnames)}')

    processing_dirs = []
    subdirs = []

    for d in dirnames:
 #       print('processing d  ' + d)
        subdirs.extend(getSubDirs(d))
        if d not in processing_dirs and d not in subdirs:
            processing_dirs.append(d)

 #       print(f'subdirs size = {len(subdirs)}')
 #       print(f'processed_dirs size = {len(processing_dirs)}')


 #   for d in processing_dirs:
 #      print(d)

 #   print(f'processed_dirs size = {len(processing_dirs)}')


#    for d in subdirs:
 #      print(d)

 #   print(f'subdirs size = {len(subdirs)}')

    return processing_dirs
