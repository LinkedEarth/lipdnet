import xlrd,os,csv
import json
from collections import OrderedDict
import flatten
import flatten_test
import validator_ch

## GLOBAL VARIABLES
finalDict = OrderedDict()

## Use this to output data columns to a csv file
## Accepts: Workbook(Obj), Sheet(str), name(str)
## Returns: None
def output_csv_datasheet(workbook, sheet, name):

    json_naming = name_to_jsonld(sheet)
    temp_sheet = workbook.sheet_by_name(sheet)
    csv_folder_and_name = str(name) + '/' + str(name) + str(json_naming) + '.csv'
    csv_full_path = 'output/' + csv_folder_and_name
    file_csv = open(csv_full_path, 'w', newline='')
    w = csv.writer(file_csv)

    try:
        ## Loop to find starting variable name
        ## Try to find if there are variable headers or not
        ref_first_var = traverse_short_row_str(temp_sheet)

        ## Traverse down to the "Missing Value" cell to get us near the data we want.
        missing_val_row = traverse_missing_value(temp_sheet)

        ## Get the missing val for search-and-replace later
        missing_val = get_missing_val(temp_sheet)

        ## Loop for 5 times past "Missing Value" to see if we get a match on the variable header
        ## Don't want to loop for too long, or we're wasting our time.
        position_start = var_headers_check(temp_sheet, missing_val_row, ref_first_var)
        data_cell_start = traverse_headers_to_data(temp_sheet, position_start)

        ## Loop over all variable names, and count how many there are. We need to loop this many times.
        first_short_cell = traverse_short_row_int(temp_sheet)
        var_limit = count_vars(temp_sheet, first_short_cell)

        ## Until we reach the bottom worksheet
        current_row = data_cell_start
        while current_row < temp_sheet.nrows:
            data_list = []

            ## Move down a row and go back to column 0
            current_column = 0

            ## Until we reach the right side worksheet
            while current_column < var_limit:

                # Increment to column 0, and grab the cell content
                cell_value = replace_missing_vals(temp_sheet.cell_value(current_row, current_column), missing_val)
                data_list.append(cell_value)
                current_column += 1
            data_list = replace_missing_vals(data_list, missing_val)
            w.writerow(data_list)
            current_row += 1

    except IndexError:
        pass

    file_csv.close()
    return

## Output the data columns from chronology sheet to csv file
## Accepts: Workbook(obj), sheet(str), name(str)
## Returns: None
# def output_csv_chronology(workbook, sheet, name):
#     json_naming = name_to_jsonld(sheet)
#     temp_sheet = workbook.sheet_by_name(sheet)
#     csv_folder_and_name = str(name) + '/' + str(name) + str(json_naming) + '.csv'
#     csv_full_path = 'output/' + csv_folder_and_name
#     file_csv = open(csv_full_path, 'w', newline='')
#     w = csv.writer(file_csv)
#
#     try:
#         total_vars = count_chron_variables(temp_sheet)
#         row = traverse_to_chron_data(temp_sheet)
#
#         while row < temp_sheet.nrows:
#
#             data_list = get_chron_data(temp_sheet, row, total_vars)
#             w.writerow(data_list)
#             row += 1
#
#     except IndexError:
#         pass
#
#     file_csv.close()
#     return

"""
MISC HELPER METHODS
"""

## Check an array to see if it is a single item or not
## Accepts: List
## Returns: Boolean
def single_item(array):
    if len(array) == 1:
        return True
    return False

## Do cell_check to see if there is any content to retrieve
## True if not empty
## False if empty
## Returns Boolean
def cell_occupied(temp_sheet, row, col):
    try:
        if temp_sheet.cell_value(row, col) != ("N/A" and " " and xlrd.empty_cell and ""):
            return True
        return False
    except IndexError:
        pass

## Convert formal titles to camelcase json_ld text that matches our context file
## Keep a growing list of all titles that are being used in the json_ld context
## Accepts: String
## Returns: String
def name_to_jsonld(title_in):

## PROBLEM HERE. NEED TO FIGURE OUT HOW TO IGNORE FLOATS AND INTS PASSING THROUGH ACCIDENTALLY

    ## Sheet names
    if title_in == 'Metadata':
        title_out = 'metadata'
    elif title_in == 'Chronology':
        title_out = 'chronology'
    elif title_in == 'Data (QC)' or title_in == 'Data(QC)':
        title_out = 'dataQC'
    elif title_in == 'Data (original)' or title_in == 'Data(original)':
        title_out = 'dataOriginal'
    elif title_in == 'Data':
        title_out = 'data'
    elif title_in == 'ProxyList':
        title_out = 'proxyList'
    elif title_in == 'About':
        title_out = 'about'

    ## Metadata variables
    elif title_in == 'DOI':
        title_out = 'pubDOI'
    elif title_in == 'Year':
        title_out = 'pubYear'
    elif title_in == 'Investigators (Lastname, first; lastname2, first2)':
        title_out = 'authors'
    elif title_in == 'Site name':
        title_out = 'siteName'
    elif 'Northernmost latitude' in title_in:
        title_out = 'latMax'
    elif 'Southernmost latitude' in title_in:
        title_out = 'latMin'
    elif 'Easternmost longitude' in title_in:
        title_out = 'longMax'
    elif 'Westernmost longitude' in title_in:
        title_out = 'longMin'
    elif title_in == 'elevation (m), below sea level negative':
        title_out = 'elevationVal'
    elif title_in == 'Collection_Name (typically a core name)':
        title_out = 'collectionName'

    ## Measurement Variables
    elif title_in == 'Method':
        title_out = 'method'
    elif title_in == 'Material':
        title_out = 'material'
    elif title_in == 'Archive':
        title_out = 'archive'
    elif title_in == 'Data_Type':
        title_out = 'dataType'
    elif title_in == 'Basis of climate relation':
        title_out = 'basis'
    elif title_in == 'Detail':
        title_out = 'detail'
    elif title_in == 'Error':
        title_out = 'error'
    elif title_in == 'Seasonality':
        title_out = 'seasonality'
    elif title_in == 'What':
        title_out = 'longName'
    elif title_in == 'Climate_intepretation_code':
        title_out = 'climateInterpretation'
    elif title_in == 'Climate_interpretation_code':
        title_out = 'climateInterpretation'
    elif title_in == 'Short_name':
        title_out = 'shortName'
    elif title_in == 'Units':
        title_out = 'units'
    elif title_in == 'notes' or title_in == 'Notes'\
            or title_in == 'Comments' or title_in == 'comments':
        title_out = 'comments'
    else:
        return

    return title_out

## Find out what type of values are stored in a specific column in data sheet
## Accepts: sheet(obj), colListNum(int)
## Returns: string
def get_data_type(temp_sheet, colListNum):

    short = traverse_short_row_str(temp_sheet)
    mv_cell = traverse_missing_value(temp_sheet)
    row = var_headers_check(temp_sheet, mv_cell, short)
    str_type = instance_str((temp_sheet.cell_value(row, colListNum-1)))
    return str_type

## Tells you what data type you have, and outputs it in string form
## Accepts: data
## Returns: string
def instance_str(cell):
    if isinstance(cell, str):
        return 'str'
    elif isinstance(cell, int):
        return 'int'
    elif isinstance(cell, float):
        return 'float'
    else:
        return 'unknown'

    ## Look for any missing values in the data_list. If you find any, replace with 'NaN'

## Accepts: data_list(list), missing_val(str)
## Returns: data_list(list)
def replace_missing_vals(cell_entry, missing_val):

    missing_val_list = ['none', 'na', '', '-', 'n/a', 'N/A', 'N/a']
    if missing_val not in missing_val_list:
        missing_val_list.append(missing_val)
    if isinstance(cell_entry, str):
        cell_entry = cell_entry.lower()
    if cell_entry in missing_val_list:
        cell_entry = 'NaN'
    return cell_entry

## Extract units from a string. In the format "elevation (meters)"
## Get the units from inside the parens
## Accepts: string
## Returns: string
def extract_units(string_in):
    start = '('
    stop = ')'
    return string_in[string_in.index(start)+1:string_in.index(stop)]

## Extract the short name from a string that also has units.
## Accepts: string
## Returns: string
def extract_short(string_in):
    stop = '('
    return string_in[:string_in.index(stop)]

"""
DATA WORKSHEET HELPER METHODS
"""

## Starts at the first short name, and counts how many variables are present
## Accepts: temp_sheet(obj), first_short(int)
## Returns: vars(int)
def count_vars(temp_sheet, first_short):
    vars = 0

    ## If we hit a blank cell, or the MV / Data cells, then stop
    while cell_occupied(temp_sheet, first_short, 0) and ("Missing" and "Data") not in temp_sheet.cell_value(first_short, 0):
        vars += 1
        first_short += 1
    return vars

## Look for what missing value is being used.
## Accepts: None
## Returns: Missing value (str)
def get_missing_val(temp_sheet):
    row = traverse_missing_value(temp_sheet)
    ## There are two blank cells to check for a missing value
    empty = ''
    missing_val = temp_sheet.cell_value(row, 1)
    missing_val2 = temp_sheet.cell_value(row, 2)
    if cell_occupied(temp_sheet, row, 1):
        if isinstance(missing_val, str):
            missing_val = missing_val.lower()
        return missing_val
    elif cell_occupied(temp_sheet, row, 2):
        if isinstance(missing_val2, str):
            missing_val2 = missing_val2.lower()
        return missing_val2
    return empty

## Traverse to short name cell in data sheet. Get the row number.
## Accepts: temp_sheet(obj)
## Returns: current_row(int)
def traverse_short_row_int(temp_sheet):
    for i in range(0, temp_sheet.nrows):
        ## We need to keep the first variable name as a reference.
        ## Then loop down past "Missing Value" to see if there is a matching variable header
        ## If there's not match, then there must not be a variable header row.
        if 'Short' in temp_sheet.cell_value(i, 0):
            current_row = i + 1
            return current_row
    return

## Traverse to short name cell in data sheet
## Accepts: temp_sheet(obj)
## Returns: first_var(str)
def traverse_short_row_str(temp_sheet):
    for i in range(0, temp_sheet.nrows):

        ## We need to keep the first variable name as a reference.
        ## Then loop down past "Missing Value" to see if there is a matching variable header
        ## If there's not match, then there must not be a variable header row.
        if 'Short' in temp_sheet.cell_value(i, 0):
            current_row = i + 1
            ref_first_var = temp_sheet.cell_value(current_row, 0)
            return ref_first_var
    return

## Traverse to missing value cell in data sheet
## Accepts: temp_sheet(obj)
## Returns: row (int)
def traverse_missing_value(temp_sheet):

    ## Traverse down to the "Missing Value" cell. This gets us near the data we want.
    for i in range(0, temp_sheet.nrows):

        ## Loop down until you hit the "Missing Value" cell, and then move down one more row
        if 'Missing' in temp_sheet.cell_value(i, 0):
            missing_row_num = i
            return missing_row_num
    return

## Traverse to the first cell that has data
## If the cell on Col 0 has content, check 5 cells to the right for content also, just to be sure.
## Accepts: temp_sheet(obj), var_headers_start(int)
## Returns: data_cell_start(int)
def traverse_headers_to_data(temp_sheet, start_cell):

    ## Start at the var_headers row, and try to find the start of the data cells
    ## Loop for 5 times. It's unlikely that there are more than 5 blank rows between the var_header row and
    ## the start of the data cells. Usually it's 1 or 2 at most.
    while not cell_occupied(temp_sheet, start_cell, 0):
        start_cell += 1
    return start_cell

## Traverse from the missing value cell to the first occupied cell
## Accepts: temp_sheet(obj), start (int)
## Returns: start(int)
def traverse_mv_to_headers(temp_sheet, start):

    ## Start at the var_headers row, and try to find the start of the data cells
    ## Loop for 5 times. It's unlikely that there are more than 5 blank rows between the var_header row and
    ## the start of the data cells. Usually it's 1 or 2 at most.
    start += 1
    ## Move past the empty cells
    while not cell_occupied(temp_sheet, start, 0):
        start += 1
    ## Check if there is content in first two cols
    ## Move down a row, check again. (Safety check)
    num = 0
    for i in range(0, 2):
        if cell_occupied(temp_sheet, start, i):
            num += 1
    start += 1
    for i in range(0, 2):
        if cell_occupied(temp_sheet, start, i):
            num += 1
    return start

## Check for matching variables first.
## If match, return var_header cell int.
## If no match, check the first two rows to see if one is all strings, or if there's some discrepancy
## Accepts: temp_sheet(obj), var_headers_start(int), ref_first_var(str)
## Returns: start_cell(int)
def var_headers_check(temp_sheet, missing_val_row, ref_first_var):
    start = traverse_mv_to_headers(temp_sheet, missing_val_row)
    ## If we find a match, then Variable headers exist for this file
    if temp_sheet.cell_value(start, 0) == ref_first_var:
        return start + 1
    ## No var match, start to manually check the first two rows and make a best guess
    else:
        col = 0
        str_row1 = 0
        str_row2 = 0

        ## Row 1
        while col < temp_sheet.ncols:
            if isinstance(temp_sheet.cell_value(start, col), str):
                str_row1 += 1
            col += 1

        ## Reset variables
        col = 0
        start += 1

        ## Row 2
        while col < temp_sheet.ncols:
            if isinstance(temp_sheet.cell_value(start, col), str):
                str_row2 += 1
            col += 1

        ## If the top row has more strings than the bottom row, then the top row must be the header
        if str_row1 > str_row2:
            return start
        ## If not, then we probably don't have a header, so move back up one row
        else:
            return start-1
    ## If we still aren't sure, traverse one row down from the MV box and start from there
    return traverse_missing_value(temp_sheet) + 1

## Traverse all cells in a row. If you find new data in a cell, add it to the list.
## Outputs a list of cell data for the specified row.
def cells_right_metadata(workbook, sheet, row, col):
    col_loop = 0
    cell_data = []
    temp_sheet = workbook.sheet_by_name(sheet)
    while col_loop < temp_sheet.ncols:
        col += 1
        col_loop += 1
        try:
            if temp_sheet.cell_value(row, col) != xlrd.empty_cell and temp_sheet.cell_value(row, col) != '':
                cell_data.append(temp_sheet.cell_value(row, col))
        except IndexError:
            continue

    return cell_data

## Traverse all cells in a column moving downward. Primarily created for the metadata sheet, but may use elsewhere
## Check the cell title, and switch it to
def cells_down_metadata(workbook, sheet, row, col):
    row_loop = 0
    special_cases = ['latMin', 'longMin', 'longMax', 'latMax', 'elevationVal', 'pubDOI', 'pubYear', 'authors']

    ## Special dictionaries to make nested block data
    lon_inner = {}
    elev_inner = {}
    lat_inner = {}
    bottomDict = {}
    pub_inner = {}

    lon_inner['units'] = 'decimalDegrees'
    lat_inner['units'] = 'decimalDegrees'
    elev_inner['units'] = 'm'
    temp_sheet = workbook.sheet_by_name(sheet)

    ## Loop until we hit the max rows in the sheet
    while row_loop < temp_sheet.nrows:
        try:
            ## If there is content in the cell...
            if temp_sheet.cell_value(row, col) != xlrd.empty_cell and temp_sheet.cell_value(row, col) != '':

                ## Convert title to correct format, and grab all data for that row
                title_formal = temp_sheet.cell_value(row, col)
                title_json = name_to_jsonld(title_formal)
                cell_data = cells_right_metadata(workbook, sheet, row, col)

                ## If we don't have a title for it, then it's not information we want to grab
                if not title_json:
                    pass

                ## Handle special block of creating GEO dictionary
                elif title_json in special_cases:
                    if title_json == 'latMax':
                        if single_item(cell_data):
                            lat_inner['max'] = cell_data[0]
                        else:
                            lat_inner['max'] = cell_data
                    elif title_json == 'latMin':
                        if single_item(cell_data):
                            lat_inner['min'] = cell_data[0]
                        else:
                            lat_inner['min'] = cell_data
                    elif title_json == 'longMax':
                        if single_item(cell_data):
                            lon_inner['max'] = cell_data[0]
                        else:
                            lon_inner['max'] = cell_data
                    elif title_json == 'longMin':
                        if single_item(cell_data):
                            lon_inner['min'] = cell_data[0]
                        else:
                            lon_inner['min'] = cell_data
                    elif title_json == 'elevationVal':
                        if single_item(cell_data):
                            elev_inner['value'] = cell_data[0]
                        else:
                            elev_inner['value'] = cell_data
                    elif title_json == 'pubDOI':
                        if single_item(cell_data):
                            pub_inner['DOI'] = cell_data[0]
                        else:
                            pub_inner['DOI'] = cell_data
                    elif title_json == 'pubYear':
                        if single_item(cell_data):
                            pub_inner['year'] = int(cell_data[0])
                        else:
                            pub_inner['year'] = cell_data
                    elif title_json == 'authors':
                        if single_item(cell_data):
                            pub_inner['authors'] = cell_data[0]
                        else:
                            pub_inner['authors'] = cell_data

                ## All other cases do not need fancy structuring
                else:
                    if single_item(cell_data):
                        bottomDict[title_json] = cell_data[0]
                    elif len(cell_data) == 0:
                        pass
                    else:
                        bottomDict[title_json] = cell_data

        except IndexError:
            continue
        row += 1
        row_loop += 1

    ## Wait until all processing is finished, then combine all GEO elements and add to final dictionary
    geo = {'longitude': lon_inner,
            'latitude': lat_inner,
            'elevation': elev_inner}
    finalDict['@context'] = "context.jsonld"
    finalDict['geo'] = geo
    finalDict['pub'] = pub_inner

    ## Add all dict items without adding in all the extra braces
    for k, v in bottomDict.items():
        finalDict[k] = v

    return

## Returns an attributes dictionary
def cells_right_datasheets(workbook, sheet, row, col, colListNum):
    temp_sheet = workbook.sheet_by_name(sheet)

    ## Iterate over all attributes, and add them to the column if they are not empty
    attrDict = OrderedDict()
    attrDict['column'] = colListNum

    ## Get the data type for this column
    attrDict['dataType'] = str(get_data_type(temp_sheet, colListNum))

    ## Separate dict for climateInterp block
    climInDict = {}

    try:
        ## Loop until we hit the right-side boundary
        while col < temp_sheet.ncols:

            ## If the cell contains any data, grab it
            if temp_sheet.cell_value(row, col) != ("N/A" and " " and xlrd.empty_cell and ""):

                title_in = name_to_jsonld(temp_sheet.cell_value(1, col))

                ## Special case if we need to split the climate interpretation string into 3 parts
                if title_in == 'climateInterpretation':
                    cicSplit = temp_sheet.cell_value(row, col).split('.')
                    climInDict['parameter'] = cicSplit[0]
                    climInDict['parameterDetail'] = cicSplit[1]
                    climInDict['interpDirection'] = cicSplit[2]

                ## Special case to add these two categories to climateInterpretation
                elif title_in == 'seasonality' or title_in == 'basis':
                    climInDict[title_in] = temp_sheet.cell_value(row, col)

                ## If the key is null, then this is a not a cell we want to add
                ## We also don't want Data Type, because we manually check for the content data type later
                ## Don't want it to overwrite the other data type.
                ## Happens when we get to the cells that are filled with formatting instructions
                ## Ex. "Climate_interpretation_code has 3 fields separated by periods..."
                elif title_in is (None or 'dataType'):
                    pass

                # All other cases, change to json-ld naming
                else:
                    contents = temp_sheet.cell_value(row, col)
                    ## Inert the variable into the attributes dictionary
                    attrDict[title_in] = contents

            ## Only add climateInterp dict if it's not empty
            if climInDict:
                attrDict['climateInterpretation'] = climInDict
            col += 1

    except IndexError:
        pass

    return attrDict

## Adds all measurement table data to the final dictionary
## Returns: None
def cells_down_datasheets(filename, workbook, sheet, row, col):

    ## Create a dictionary to hold each column as a separate entry
    measTableDict = OrderedDict()

    ## Iterate over all the short_name variables until we hit the "Data" cell, or until we hit an empty cell
    ## If we hit either of these, that should mean that we found all the variables
    ## For each short_name, we should create a column entry and match all the info for that column
    temp_sheet = workbook.sheet_by_name(sheet)
    measTableName = name_to_jsonld(sheet)
    columnsTop = []
    commentList = []
    colListNum = 1

    ## Loop downward until you hit the "Data" box
    try:
        while temp_sheet.cell_value(row, col) != 'Data':

            variable = name_to_jsonld(temp_sheet.cell_value(row, col))

            ## If the cell isn't blank or empty, then grab the data
            ## Special case for handling comments since we want to stop them from being inserted at column level
            if variable == 'comments':
                for i in range(1, 3):
                    if cell_occupied(temp_sheet, row, i):
                        commentList.append(temp_sheet.cell_value(row, i))

            ## All other cases, create a list of columns, one dictionary per column
            elif temp_sheet.cell_value(row, col) != ('' and xlrd.empty_cell):
                columnsTop.append(cells_right_datasheets(workbook, sheet, row, col, colListNum))
                colListNum += 1
            row += 1

    except IndexError:
        pass

    ## Add all our data pieces for this column into a new entry in the Measurement Table Dictionary
    measTableDict['measTableName'] = measTableName
    measTableDict['filename'] = str(filename) + str(measTableName) + ".csv"

    ## If comments exist, insert them at table level
    if commentList:
        measTableDict['comments'] = commentList[0]
    measTableDict['columns'] = columnsTop

    ## Reset list back to null for next loop
    commentList = []
    return measTableDict

"""
CHRONOLOGY HELPER METHODS
"""

## Traverse down to the row that has the first variable
## Accepts: temp_sheet(obj)
## Returns: row (int)
def traverse_to_chron_var(temp_sheet):
    row = 0
    while 'Chronology' in temp_sheet.cell_value(row, 0):
        row += 1
    if temp_sheet.cell_value(row+1, 0):
        while temp_sheet.cell_value(row, 0) == '':
            row += 1
    return row

## Count the number of chron variables:
## Accepts: temp_sheet(obj)
## Returns: total_count(int)
def count_chron_variables(temp_sheet):
    total_count = 0
    start_row = traverse_to_chron_var(temp_sheet)
    while temp_sheet.cell_value(start_row, 0) != '':
        total_count += 1
        start_row += 1
    return total_count

## Capture all the vars in the chron sheet (for json-ld output)
## Accepts: sheet, start_row(int)
## Returns: column data (list of dicts)
def get_chron_var(temp_sheet, start_row):
    col_dict = OrderedDict()
    out_list = []
    column = 1
    while temp_sheet.cell_value(start_row, 0) != '':

        short_cell = temp_sheet.cell_value(start_row, 0)
        long_cell = temp_sheet.cell_value(start_row, 1)
        print(long_cell)
        ## If there are parenthesis (units) in this cell, capture the units
        if ('(' or ')') in short_cell:
            units = extract_units(short_cell)
            short_name = extract_short(short_cell)

        ## else, this cell is unitless. Just capture the short name.
        else:
            units = 'none'
            short_name = short_cell

        ## Grab the long name. We have units from the short cell, so if there are units in the long_cell also,
        ## then extract only the long_name and trash the units.
        if ('(' or ')') in long_cell:
            long_name = extract_short(long_cell)
        else:
            long_name = long_cell

        ## Fill the dictionary for this column
        col_dict['column'] = column
        col_dict['shortName'] = short_name
        col_dict['longName'] = long_name
        col_dict['units'] = units
        out_list.append(col_dict.copy())
        start_row += 1
        column += 1

    return out_list

## Traverse down to the first row that has chron data
## Accepts: temp_sheet(obj)
## Returns: row(int)
def traverse_to_chron_data(temp_sheet):
    traverse_row = traverse_to_chron_var(temp_sheet)
    reference_var = temp_sheet.cell_value(traverse_row, 0)

    ## Traverse past all the short_names, until you hit a blank cell (the barrier)
    while temp_sheet.cell_value(traverse_row, 0) != '':
        traverse_row += 1
    ## Traverse past the empty cells until we hit the chron data area
    while temp_sheet.cell_value(traverse_row, 0) == '':
        traverse_row += 1

    ## Check if there is a header row. If there is, move past it. We don't want that data
    if temp_sheet.cell_value(traverse_row, 0) == reference_var:
        traverse_row += 1

    return traverse_row

## Capture all data in for a specific chron data row (for csv output)
## Accepts: temp_sheet(obj), row(int), total_vars(int)
## Returns: data_row(list)
def get_chron_data(temp_sheet, row, total_vars):

    data_row = []
    missing_val_list = ['none', 'na', '', '-']
    for i in range(0, total_vars):
        cell = temp_sheet.cell_value(row, i)
        if isinstance(cell, str):
            cell = cell.lower()
        if cell in missing_val_list:
            cell = 'NaN'
        data_row.append(cell)
    return data_row


"""
PARSER
"""
def parser():

    ## Ask the user if their excel files are in the current directory, or to specify a file path
    default_path = '/Users/nick/Dropbox/GeochronR/ExcelInputToParse/Australasia'
    print("Are your files stored in the current 'xlsfiles' directory? (y/n)")
    answer = input()
    print("\n")

    # Specify a directory path
    if answer is "n":
        print("Please specify the path where your files are stored: ")
        print("(Ex: /Users/chrisheiser1/Desktop or /Users/chrisheiser1/Dropbox/GeoChronR/ExcelInputToParse)")
        user_path = input()
        os.chdir(user_path)

    # Use current directory
    else:
        os.chdir(default_path)

    ## Add all excel files from user-specified directory, or from current directory
    ## Puts all file names in a list we iterate over
    excel_files = []
    for file in os.listdir():
        if file.endswith(".xls") or file.endswith(".xlsx"):
            excel_files.append(file)


    datasheetNameList = []
    # ## Loop over all the lines (filenames) that are in the txt file
    print("Processing files: ")
    for current_file in excel_files:
        print(current_file)

        ## For our current excel workbook, set each worksheet to a variable
        ## Set worksheet variables dynamically, based on the worksheet name
        workbook = xlrd.open_workbook(current_file)

        ## Most common sheets. If find sheet with matching name, set to variable
        for sheet in workbook.sheet_names():
            new_name = name_to_jsonld(sheet)
            # data_original_str = None
            # data_qc_str = None
            # data_str = None

            if sheet == 'Metadata':
                metadata = workbook.sheet_by_index(workbook.sheet_names().index('Metadata'))
                metadata_str = 'Metadata'
            elif sheet == 'Chronology':
                chronology = workbook.sheet_by_index(workbook.sheet_names().index('Chronology'))
                chronology_str = 'Chronology'
            elif 'Data' in sheet:
                # data_qc = workbook.sheet_by_index(workbook.sheet_names().index(sheet))
                # data_qc_str = sheet
                datasheetNameList.append(sheet)
            # elif sheet == 'Data(QC)':
            #     data_qc = workbook.sheet_by_index(workbook.sheet_names().index('Data(QC)'))
            #     data_qc_str = 'Data(QC)'
            #     datasheetNameList.append(data_qc_str)
            # elif sheet == 'Data (original)':
            #     data_original = workbook.sheet_by_index(workbook.sheet_names().index('Data (original)'))
            #     data_original_str = 'Data (original)'
            #     datasheetNameList.append(data_original_str)
            # elif sheet == 'Data(original)':
            #     data_original = workbook.sheet_by_index(workbook.sheet_names().index('Data(original)'))
            #     data_original_str = 'Data(original)'
            #     datasheetNameList.append(data_original_str)
            elif new_name == 'ProxyList':
                proxyList = workbook.sheet_by_index(workbook.sheet_names().index('ProxyList'))
                proxyList_str = 'ProxyList'
            elif sheet == 'About':
                about = workbook.sheet_by_index(workbook.sheet_names().index('About'))
                about_str = 'About'
            elif sheet == 'Data':
                data = workbook.sheet_by_index(workbook.sheet_names().index('Data'))
                data_str = 'Data'
                datasheetNameList.append(data_str)


        # Naming scheme
        # Use whatever string name comes before the file extension
        name = current_file

        if 'xlsfiles/' in name:
            name = name[9:]
        if '.xls' in name:
            name = name[:-4]
        if '.xlsx' in name:
            name = name[:-5]
        if '.' in name:
            name = name[:-1]

###########################
## METADATA WORKSHEETS   ##
###########################

        ## Run the method for adding metadata info to finalDict
        cells_down_metadata(workbook, metadata_str, 0, 0)

###########################
##   DATA WORKSHEETS     ##
###########################

        ## Need to handle cases where there is Data_QC, Data_original, or Data, or a combination of them.
        combined = []

        ## Loop over the data sheets we know exist
        for sheet_str in datasheetNameList:
            sheet_str = cells_down_datasheets(name, workbook, sheet_str, 2, 0)
            combined.append(sheet_str)

        ## Add all dict items without adding in all the extra braces
        finalDict['measurements'] = combined

###########################
## CHRONOLOGY WORKSHEETS ##
###########################

        # chronTableName = metadata.cell_value(30, 1)
        #
        # if chronology:
        #     start_row = traverse_to_chron_var(chronology)
        #     columns_list_chron = get_chron_var(chronology, start_row)
        #
        # ## Create a top level Chronology dictionary so we can give it a key
        # chronDict = {}
        # chronDict['chronTableName'] = chronTableName
        # chronDict['filename'] = str(name) + str(chronTableName) + '.csv'
        # chronDict['columns'] = columns_list_chron
        # finalDict['chronology'] = chronDict

############################
## FILE NAMING AND OUTPUT ##
############################

        ## Combine everything we have into the final dictionary

        ## Creates the directory 'output' if it does not already exist
        if not os.path.exists('output/' + str(name)):
              os.makedirs('output/' + str(name))

        ## CSV - DATA
        for sheet_str in datasheetNameList:
            output_csv_datasheet(workbook, sheet_str, name)
        del datasheetNameList[:]

        ## CSV - CHRONOLOGY
        # output_csv_chronology(workbook, chronology_str, name)

        ## JSON LD
        ## PROBLEM WITH OUTPUTTING THE CORRECT FILE NAME FOR JSON LD FILE NAMES
        new_file_name_jsonld = str(name) + '/' + str(name) + '.jsonld'
        file_jsonld = open('output/' + new_file_name_jsonld, 'w')
        file_jsonld = open('output/' + new_file_name_jsonld, 'r+')

        ## Write finalDict to json-ld file with dump
        ## Dump outputs into a readable json hierarchy
        json.dump(finalDict, file_jsonld, indent=4)

        ## Flatten the JSON LD file, and output it to its own file
        flattened_file = flatten.run(finalDict)
        new_file_flat_json = str(name) + '/' + str(name) + '_flat.json'
        file_flat_jsonld = open('output/' + new_file_flat_json, 'w')
        file_flat_jsonld = open('output/' + new_file_flat_json, 'r+')
        json.dump(flattened_file, file_flat_jsonld, indent=0)

parser()