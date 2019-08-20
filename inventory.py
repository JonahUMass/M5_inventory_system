# client generator: https://console.developers.google.com/apis/credentials?project=m5-inventory-system&supportedpurview=project
#make a service client

#THIS FILE IS SUBJECT TO SERIOUS CHANGE!

"""
planning:
-add new item
-add new type
-change item
-change type
-checkout item
-checkin item
-log action
"""

import gspread, time, pickle
from oauth2client.service_account import ServiceAccountCredentials

def singleton(cls):
    return cls()

# use creds to create a client to interact with the Google Drive API
scope = ['https://spreadsheets.google.com/feeds', # this list defines waht you are authorized ot acess
         'https://www.googleapis.com/auth/drive'] #EX: this line says ' i'm allowed to see drive'
creds = ServiceAccountCredentials.from_json_keyfile_name('m5-inventory-system-eadb8680e0cb.json', scope)
client = gspread.authorize(creds)

try:
    jar = pickle.load(open('_saved_drive_sheets.pickle', 'rb'))
    type_sheet = jar[0]
    type_sheet.row_values(1)# test if credentials are dtill valid

    uid_sheet = jar[1]
    uid_sheet.row_values(1)# test if credentials are dtill valid

    print('unpickled')
except:
    print('unpicled FAILED making new version')
    type_sheet = client.open("M5_TypeIDs").sheet1
    uid_sheet = client.open("M5_UIDs").sheet1
    checkin_sheet = client.open("M5_Auto_Checkin").sheet1
    pickle.dump([type_sheet, uid_sheet], open('_saved_drive_sheets.pickle', 'wb'))

#@singleton
class uid_indices:
    _uid_header = uid_sheet.row_values(1)
    length = uid_sheet.col_count

    uid                     = _uid_header.index('UID:') + 1
    type_id                 = _uid_header.index('TypeID:') + 1
    specific_location       = _uid_header.index('Specific Location:') + 1
    extra_tags              = _uid_header.index('Extra Tags:') + 1
    is_broken               = _uid_header.index('Is Broken:') + 1
    is_checked_out          = _uid_header.index('Is Checked Out:') + 1
    last_time_checked_out   = _uid_header.index('Last Time Checked Out:') + 1
    last_person_checked_out = _uid_header.index('Last Person Checked Out:') + 1

    del _uid_header

#@singleton
class type_indices:
    _type_header = type_sheet.row_values(1)
    length = type_sheet.col_count

    type_id       = _type_header.index('TypeID:') + 1
    display_name  = _type_header.index('Display Name:') + 1
    locations     = _type_header.index('Locations:') + 1
    tags          = _type_header.index('Tags:') + 1
    description   = _type_header.index('Description:') + 1
    vendors       = _type_header.index('Vendors:') + 1
    makers         = _type_header.index('Makers:') + 1
    purchase_urls = _type_header.index('Purchase URLs:') + 1

    del _type_header

class check_indices:
    _check_header = check_sheet.row_values(1)

def int_to_id(num):
    id = hex(num)
    while len(id) < 6:
        id = id[0:2] + '0' + id[2:]
    return id

def id_to_int(string):
    return int(string, 16)


def add_type_id(name, locations, tags, description = 'No_Description_Provided',
                vendors = 'No_vendors_Provided', makers= 'No_Makers_Provided',
                purchase_urls = 'No_URLs_Provided'):

    if type(locations) == str:
        locations = (locations,)
    if type(vendors) == str:
        vendors = (vendors,)
    if type(purchase_urls) == str:
        purchase_urls = (purchase_urls,)
    if type(makers) == str:
        makers = (makers,)

    type_col_values = type_sheet.col_values(type_indices.type_id)

    #find the lowest pos empty row
    y_index = len(type_col_values) # index after end of list

    #print(type_sheet.row_count, type_indices.type_id)
    #print(type_sheet.cell(type_sheet.row_count, type_indices.type_id).value)
    last_id = id_to_int(type_col_values[-1])

    # make a list to represent the row with an empty space in front
    #space is in forn so the indexing for the sheet and list are the same
    #just pop one cell of the front before writing
    new_row = ['']*(type_indices.length +1)

    # set type id

    new_row[type_indices.type_id] = int_to_id(last_id+1)

    # set name
    new_row[type_indices.display_name] =name

    # set name
    location_str = ' '.join([location.lower() for location in locations])
    new_row[type_indices.locations] = location_str

    # set name
    new_row[type_indices.tags] = ' '.join([tag.lower() for tag in tags])

    # set vendors
    new_row[type_indices.vendors] = ' '.join(vendors)

    #set maker
    new_row[type_indices.makers] = ' '.join(makers)

    # set description
    new_row[type_indices.description] = description

    # set purchase urls
    new_row[type_indices.purchase_urls] = ' '.join(purchase_urls)

    #trim end
    while new_row[-1] == '':
        new_row.pop(-1)

    #get rif of leading empty cell
    new_row.pop(0)

    type_sheet.insert_row(new_row, y_index + 1)

    return last_id + 1

def add_unique_item(uid, type_id, specific_location = '',
                    extra_tags = '',	is_broken = ''):
    """
    desc: a function to call to google sheets and add a new uid item to the spreadsheet.
    arg uid: The unique item id number represented as a hex string "0x0af3" or an int of the equivalent value;
    arg type_id: the type of the new item, search the type id spradsheet for the corresponding number;
    kwarg specific_location: a string representing the M5 location where the item will be stored. EX: ID3;
    """
    if type(extra_tags) == str:
        locations = (extra_tags,)

    y_index = 1
    while uid_sheet.cell(y_index, uid_indices.uid).value != '':
        y_index += 1

    # make sure bath are hex strings of proper length
    if type(uid) == int:
        uid_str = hex(uid)
    else:
        uid_str = uid
    while len(uid_str) < 6:
        uid_str = uid_str[0:2] + '0' + uid_str[2:]

    if type(type_id) == int:
        type_id_str = hex(type_id)
    else:
        type_id_str = type_id
    while len(type_id_str) < 6:
        type_id_str = type_id_str[0:2] + '0' + type_id_str[2:]

    # makse sure no duplicates exist
    if uid_str in uid_sheet.col_values(uid_indices.uid):
        raise ValueError('UID already registered')

    #make sure type id exists
    if not type_id_str in type_sheet.col_values(type_indices.type_id):
        raise ValueError('Invalid Type ID')

    # start writing data
    new_row = ['']*(uid_indices.length + 1)

    new_row[uid_indices.uid] = uid_str
    new_row[uid_indices.type_id] = type_id_str
    #new_row[uid_indices.]

    # remove trailing empty cellss
    while new_row[-1] == '':
        new_row.pop(-1)

    # remove lagging empty cellss
    new_row.pop(0)

    uid_sheet.insert_row(new_row, y_index)
'''
#time.sleep(200)
"""for i in range(0x0b, 0x013):
    try:
        add_unique_item(i, 0x0)
    except Exception as e:
        print(e)"""

add_type_id('Usb Wifi Dongle', 'ob2',
            ('wifi','usb', 'generic', 'dongle'),
            makers = ('various'),
            #vendors = ('amazon', 'adafruit', 'PJRC'),
            #purchase_urls = 'https://www.pjrc.com/teensy/',
            )'''
