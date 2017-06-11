# This code logs keystrokes IN THIS JUPYTER NOTEBOOK WINDOW ONLY
# Keys are written as CSV, in format:
#         machine_id, delta_t, duration_t, keycode
# to the file ../jupyter_keylog.csv
# Run both this cell and the following one!
import platform, hashlib, os, time
def get_random_id():
    sha = hashlib.sha256()
    sha.update("-".join(platform.uname()))
    sha.update("%.8f"%time.time())
    sha.update("%.8f"%time.clock())
    try:
        sha.update(os.urandom(200))
    except NotImplementedError:
        print "No system random..."
    return sha.hexdigest()

def get_unique_id():
    try:
        with open("../unique.id") as f:
            unique_id = f.readline()
            return unique_id.strip()
    except IOError:
        with open("../unique.id", "w") as f:
            unique_id = get_random_id()
            f.write("%s\n"%unique_id)
        return unique_id

def js_key_update(seq):
    unique_id = int(get_unique_id(), base=16) & ((2**31)-1)    
    with open("../jupyter_keylog.csv", "a+") as f:        
        for key, t, up in zip(seq[0:-2:3], seq[1:-1:3], seq[2::3]):
            f.write("%s, %s, %s, %s\n" % (unique_id, t, up, key))