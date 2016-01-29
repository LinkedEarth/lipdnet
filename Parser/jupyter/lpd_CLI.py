import cmd

from Parser.jupyter.lpd_library import *

"""
Notes:
- Command arguments are in the form of: "loadLiPD /path/goes/here"
- all commands must have (self, arg) parameters at a minimum.
"""

class LiPD_CLI(cmd.Cmd):
    intro = "Welcome to LiPD. Type help or ? to list commands.\nSet the current working directory before proceeding\n"
    prompt = '(lipd) '

    def __init__(self):
        cmd.Cmd.__init__(self)
        self.llib = LiPD_Library()

    def do_setCWD(self, path):
        """
        Set the current working directory by providing a directory path.
        (ex. /Path/to/files)
        :param path: (str) Directory path
        """
        self.llib.setDir(path)

    def do_loadLipd(self, filename):
        """
        Load a single LiPD file into the workspace. File must be located in the current working directory.
        (ex. loadLiPD NAm-ak000.lpd)
        :param filename: (str) LiPD filename
        """
        self.llib.loadLipd(filename)

    def do_loadLipds(self, arg):
        """
        Load all LiPD files in the current working directory into the workspace.
        """
        self.llib.loadLipds()

    def do_displayLipd(self, filename):
        """
        Display the contents of the specified LiPD file. (Must be previously loaded into the workspace)
        (ex. displayLiPD NAm-ak000.lpd)
        :param filename: (str) LiPD filename
        """
        self.llib.displayLipd(filename)

    def do_displayFiles(self, arg):
        """
        Prints filenames of all LiPD files currently loaded in the workspace.
        """
        self.llib.displayLipds()

    def do_saveLipd(self, filename):
        """
        Saves changes made to the target LiPD file.
        (ex. saveLiPD NAm-ak000.lpd)
        :param filename: (str) LiPD filename
        """
        self.llib.saveLipd(filename)

    def do_saveLipds(self, arg):
        """
        Save changes made to all LiPD files in the workspace.
        """
        self.llib.saveLipds()

    def do_quit(self, arg):
        """
        Quit and exit the program. (Does not save changes)
        """
        self.llib.close()
        return True

    def do_displayCSV(self, filename):
        self.llib.displayLipdCSV(filename)


# if __name__ == '__main__':
LiPD_CLI().cmdloop()