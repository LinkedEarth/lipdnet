from geoChronR.Parser.misc.bag import *
from geoChronR.Parser.misc.directory import *
from geoChronR.Parser.misc.zips import *
from geoChronR.Parser.doi.doi_resolver import *

__author__ = 'Chris Heiser'
"""
PURPOSE: Take .lpd file(s) that have been bagged with Bagit, and compressed (zip). Uncompress and unbag,
read in the DOI from the jsonld file, invoke DOI resolver script, retrieve doi.org info with given DOI,
update jsonld file, Bag the files, and compress the Bag. Output a txt log file with names and errors of
problematic files.

CHANGELOG
Version 1.0 / 12.08.2015 / Chris

Input:  .lpd file (Zip containing a Bag)
Output: .lpd file (Zip containing a Bag)

"""


def dir_cleanup(dir_bag, dir_data):
    """

    :param dir_bag: (str) Path to root of Bag
    :param dir_data: (str) Path to Bag /data subdirectory
    :return: None
    """

    # dir : dir_data -> dir_bag
    os.chdir(dir_bag)

    # Delete files in dir_bag
    for file in os.listdir(dir_bag):
        if file.endswith('.txt'):
            os.remove(os.path.join(dir_bag, file))

    # Move dir_data files up to dir_bag
    for file in os.listdir(dir_data):
        shutil.move(os.path.join(dir_data, file), dir_bag)

    # Delete empty dir_data folder
    shutil.rmtree(dir_data)

    return


def process_lpd(name, path_tmp):
    """
    Opens up a jsonld file, invokes doi_resolver, closes file, updates changelog, cleans directory, and makes new bag.
    :param name: (str) Name of current .lpd file
    :param path_tmp: (str) Path to tmp directory
    :return: none
    """

    dir_root = os.getcwd()
    dir_bag = os.path.join(path_tmp, name)
    dir_data = os.path.join(dir_bag, 'data')

    # Navigate down to jLD file
    # dir : dir_root -> dir_data
    os.chdir(dir_data)

    # Open jld file and read in the contents. Execute DOI Resolver.
    with open(os.path.join(dir_data, name + '.jsonld'), 'r') as jld_file:
        jld_data = json.load(jld_file)

    DOIResolver(dir_root, name, jld_data).start()

    # Open the jld file and overwrite the contents with the new data.
    with open(os.path.join(dir_data, name + '.jsonld'), 'w+') as jld_file:
        json.dump(jld_data, jld_file, indent=2, sort_keys=True)

    # except ValueError:
    #     txt_log(dir_root, 'quarantine.txt', name, "Invalid Unicode characters. Unable to load file.")

    # jld_file.close()

    # Open changelog. timestamp it. Prompt user for short description of changes. Close and save
    update_changelog()

    # Delete old bag files, and move files to root for re-bagging
    # dir : dir_data -> dir_bag
    dir_cleanup(dir_bag, dir_data)

    # Create a bag for the 3 files
    new_bag = create_bag(dir_bag)
    open_bag(dir_bag)

    new_bag.save(manifests=True)

    return


def main():
    """
    Main function that controls the script. Take in directory containing the .lpd file(s). Loop for each file.
    :return: None
    """
    # Take in user-chosen directory path
    dir_root = '/Users/chrisheiser1/Desktop/test'

    # Find all .lpd files in current directory
    # dir: ? -> dir_root
    os.chdir(dir_root)
    f_list = list_files('.lpd')

    for name_ext in f_list:
        print('processing: {}'.format(name_ext))

        # .lpd name w/o extension
        name = os.path.splitext(name_ext)[0]

        # Unzip file and get tmp directory path
        dir_tmp = unzip(name_ext)

        # Unbag and check resolved flag. Don't run if flag exists
        if resolved_flag(open_bag(os.path.join(dir_tmp, name))):
            print("DOI previously resolved. Next file...")
            shutil.rmtree(dir_tmp)

        # Process file if flag does not exist
        else:
            # dir: dir_root -> dir_tmp
            process_lpd(name, dir_tmp)
            # dir: dir_tmp -> dir_root
            os.chdir(dir_root)
            # Zip the directory containing the updated files. Created in dir_root directory
            re_zip(dir_tmp, name, name_ext)
            os.rename(name_ext + '.zip', name_ext)
            # Cleanup and remove tmp directory
            shutil.rmtree(dir_tmp)
    print("Remember: Quarantine.txt contains a list of errors that may have happened during processing.")
    return

main()