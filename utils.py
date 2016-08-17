import sys
import os

# Under python 3 we need to import exceptions
if sys.version_info < (3, 0):
    from exceptions import IndexError, NameError


def get_base():
    '''get_base returns the project folder base. If the user is using Ipython, we set that
    to be the present working directory
    '''
    try:
        __IPYTHON__
        try:
            base
        except:
            raise Exception('you must set "base" to the base variable ')
    except NameError:
        __IPYTHON__=False
        try:
            base=sys.argv[1]
        except IndexError:
            print("You must specify a base project directory as your first argument.")
            sys.exit()
    print("BASE project directory is defined as %s" %(base))
    return base


def get_pwd():
    '''get_pwd gets the present working directory of the scripts'''
    if __IPYTHON__:
        return os.getcwd()
    else:
        return os.path.dirname(os.path.abspath(__file__))


def make_dirs(folders,reason=""):
    '''make directories if they don't exist'''
    if not isinstance(folders,list):
        folders = [folders]
    for folder in folders:
        if not os.path.exists(folder):
            print("Creating directory %s %s" %(folder,reason)) 
            os.mkdir(folder)
