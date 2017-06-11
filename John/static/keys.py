from collections import defaultdict

codes = {
"backspace" : 8,
"tab" : 9,
"enter" : 13,
"shift" : 16,
"ctrl" : 17,
"alt" : 18,
"pause/break" : 19,
"caps lock" : 20,
"escape" : 27,
"(space)" : 32,
"page up" : 33,
"page down" : 34,
"end" : 35,
"home" : 36,
"left arrow" : 37,
"up arrow" : 38,
"right arrow" : 39,
"down arrow" : 40,
"insert" : 45,
"delete" : 46,
"0" : 48,
"1" : 49,
"2" : 50,
"3" : 51,
"4" : 52,
"5" : 53,
"6" : 54,
"7" : 55,
"8" : 56,
"9" : 57,
"a" : 65,
"b" : 66,
"c" : 67,
"d" : 68,
"e" : 69,
"f" : 70,
"g" : 71,
"h" : 72,
"i" : 73,
"j" : 74,
"k" : 75,
"l" : 76,
"m" : 77,
"n" : 78,
"o" : 79,
"p" : 80,
"q" : 81,
"r" : 82,
"s" : 83,
"t" : 84,
"u" : 85,
"v" : 86,
"w" : 87,
"x" : 88,
"y" : 89,
"z" : 90,
"left window key" : 91,
"right window key" : 92,
"select key" : 93,
"numpad 0" : 96,
"numpad 1" : 97,
"numpad 2" : 98,
"numpad 3" : 99,
"numpad 4" : 100,
"numpad 5" : 101,
"numpad 6" : 102,
"numpad 7" : 103,
"numpad 8" : 104,
"numpad 9" : 105,
"multiply" : 106,
"add" : 107,
"subtract" : 109,
"decimal point" : 110,
"divide" : 111,
"f1" : 112,
"f2" : 113,
"f3" : 114,
"f4" : 115,
"f5" : 116,
"f6" : 117,
"f7" : 118,
"f8" : 119,
"f9" : 120,
"f10" : 121,
"f11" : 122,
"f12" : 123,
"num lock" : 144,
"scroll lock" : 145,
"semi-colon" : 186,
"equal sign" : 187,
"comma" : 188,
"dash" : 189,
"period" : 190,
"forward slash" : 191,
"grave accent" : 192,
"open bracket" : 219,
"back slash" : 220,
"close braket" : 221,
"single quote" :222
}


        
locations = {
"backspace" : 8,
"tab" : 9,
"enter" : 13,
"shift" : 16,
"ctrl" : 17,
"alt" : 18,
"pause/break" : 19,
"caps lock" : 20,
"escape" : 27,
"(space)" : 32,
"page up" : 33,
"page down" : 34,
"end" : 35,
"home" : 36,
"left arrow" : 37,
"up arrow" : 38,
"right arrow" : 39,
"down arrow" : 40,
"insert" : 45,
"delete" : 46,
"0" : 48,
"1" : 49,
"2" : 50,
"3" : 51,
"4" : 52,
"5" : 53,
"6" : 54,
"7" : 55,
"8" : 56,
"9" : 57,
"a" : 65,
"b" : 66,
"c" : 67,
"d" : 68,
"e" : 69,
"f" : 70,
"g" : 71,
"h" : 72,
"i" : 73,
"j" : 74,
"k" : 75,
"l" : 76,
"m" : 77,
"n" : 78,
"o" : 79,
"p" : 80,
"q" : 81,
"r" : 82,
"s" : 83,
"t" : 84,
"u" : 85,
"v" : 86,
"w" : 87,
"x" : 88,
"y" : 89,
"z" : 90,
"left window key" : 91,
"right window key" : 92,
"select key" : 93,
"numpad 0" : 96,
"numpad 1" : 97,
"numpad 2" : 98,
"numpad 3" : 99,
"numpad 4" : 100,
"numpad 5" : 101,
"numpad 6" : 102,
"numpad 7" : 103,
"numpad 8" : 104,
"numpad 9" : 105,
"multiply" : 106,
"add" : 107,
"subtract" : 109,
"decimal point" : 110,
"divide" : 111,
"f1" : 112,
"f2" : 113,
"f3" : 114,
"f4" : 115,
"f5" : 116,
"f6" : 117,
"f7" : 118,
"f8" : 119,
"f9" : 120,
"f10" : 121,
"f11" : 122,
"f12" : 123,
"num lock" : 144,
"scroll lock" : 145,
"semi-colon" : 186,
"equal sign" : 187,
"comma" : 188,
"dash" : 189,
"period" : 190,
"forward slash" : 191,
"grave accent" : 192,
"open bracket" : 219,
"back slash" : 220,
"close braket" : 221,
"single quote" :222
}


numpad = [
"numpad 0",
"numpad 1",
"numpad 2",
"numpad 3",
"numpad 4",
"numpad 5",
"numpad 6",
"numpad 7",
"numpad 8",
"numpad 9",
]


function = [
"f1",
"f2", 
"f3",
"f4", 
"f5", 
"f6", 
"f7", 
"f8", 
"f9", 
"f10", 
"f11", 
"f12", 
]


ext_numpad = numpad + ["multiply",
"add",
"subtract",
"decimal point",
"divide"]

locks = ["num lock","scroll lock", "pause/break"]

special = ["left window key",
"right window key",
"select key"
]

arrows = ["left arrow",
"up arrow",
"right arrow",
"down arrow"]

home_end = ["end",
"home"]

page = ["page up",
"page down"]

nav = arrows + home_end + page

insert_delete = ["insert",
"delete"]

top_block = insert_delete + home_end + page

f_block = function + ["escape"]

backspace = ["backspace"]

delchar = ['backspace', 'delete']

enter = ['enter']

modifier = ['shift', 'ctrl', 'alt']

shifts = ['shift', 'caps lock']
caps_lock = ['caps lock']
all_locks = locks + ['caps lock']

tab = ['tab']
whitespace = ['(space)', 'tab', 'enter']

web_nav = ['tab', 'esc', 'enter', 'backspace']



nonprint = locks + arrows + top_block + f_block + web_nav





numbers = [
"0" ,
"1" ,
"2" ,
"3" ,
"4" ,
"5" ,
"6" ,
"7" ,
"8" ,
"9" ,
]


editing = delchar + ['enter'] + insert_delete

letters = list('abcdefghijklmnopqrstuvwxyz')

punct = [
"equal sign",
"comma",
"dash",
"period",
"forward slash",
"grave accent",
"open bracket",
"back slash",
"close braket",
"single quote",
]

character_keys = numbers + punct + letters + ['(space)']


key_types = {"allkeys":codes.keys(),
"numpad":numpad,
"function":function,
"ext_numpad":ext_numpad,
"locks":locks,
"special":special,
"arrows":arrows,
"home_end":home_end,
"page":page,
"nav":nav,
"insert_delete":insert_delete,
"top_block":top_block,
"f_block":f_block,
"backspace":backspace,
"delchar":delchar,
"enter":enter,
"modifier":modifier,
"shifts":shifts,
"caps_lock":caps_lock,
"all_locks":all_locks,
"tab":tab,
"whitespace":whitespace,
"web_nav":web_nav,
"nonprint":nonprint,
"numbers":numbers,
"editing":editing,
"letters":letters,
"punct":punct,
"character_keys":character_keys}

inv_codes = {v:k for k,v in codes.items()}

def get_key_types():
    """Return all known key types"""
    return key_types.keys()
    
def key_to_name(keys):
    return [inv_codes.get(k, None) for k in keys]
    
    
def classify_keys(keys, classes):
    names = key_to_name(keys)
    class_index = defaultdict(list)
    for i,cls in enumerate(classes):
        types = key_types.get(cls, [])
        for type in types:
            class_index[type].append(i)
        
    return [class_index.get(name, []) for name in names]
            
        


