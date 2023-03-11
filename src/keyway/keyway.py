import sqlite3
import sys
import os
import base64
from cryptography.fernet import Fernet

# the main keyway class
# By default, keys are stored in the active environment folder
# Never upload your virtual environment to github. 
# If you must, set a custom path like:
#   keyway = Keyway(path = "your/custom/path")
# you can also optionally set a user like: 
#   keyway = Keyway(user = "username")
class Keyway(dict):
    
    # initialize class
    def __init__(self, 
                 user = "default", # seperates keys into tables 
                 path = None, 
                 db_name = "keyway",
                 use_all = True):
        
        # set db name and use_all flag
        self._db_name = db_name
        self._use_all = use_all
        
        # append "user_" to the table name to prevent 
        # accidentally using reserved words
        self._table_name = "user_" + user
        
        # set database's path
        if path is None:
            
            # if no custom path is provided, store keys in the active environment
            self._env_path = sys.prefix
            if hasattr(sys, 'real_prefix'):
                self._env_path = sys.real_prefix
            self._env_path = os.path.abspath(self._env_path).replace("\\","/")
            if not self._env_path.endswith("/"):
                self._env_path += "/"
        
        else:
            # set custom path
            self._env_path = path
        
        # keys are encrypted with a fernet cipher of the environment location.
        # not super secure, but better than plaintext.
        # the database's encryption will break if moved from its original location.
        # keyway is only as secure as your environment, so as long 
        # as your environment is not uploaded to github, you will be fine
        key = ((self._env_path + self._table_name + ("a" * 100))[:32]).encode("utf-8")
        key = base64.urlsafe_b64encode(key)    
        self._f = Fernet(key)
        
        # create empty table if not exists
        self._create()
    
    # SQLITE FUNCTIONS
      
    # connect to the sqlite table
    def _connect(self):
        self.conn = sqlite3.connect(f"{self._env_path}{self._db_name}.db")
        self.cur = self.conn.cursor()
    
    # close the sqlite connection
    def _close(self):
        self.conn.close()
        
    # execute a sqlite command    
    def _execute(self, query):
        self._connect()
        self.cur.execute(query)
        self.conn.commit()
        self._close()
    
    # fetch all sqlite results
    def _fetchall(self, query):
        self._connect()
        self.cur.execute(query)
        result = self.cur.fetchall()
        self._close()
        return result
 
    # create empty table if not exists
    def _create(self):
        self._execute(f"""
            CREATE TABLE IF NOT EXISTS
            {self._table_name} ("key" TEXT,
                "value" TEXT,
                PRIMARY KEY ("key"))                         
            """)

    # CRYPTOGRAPHY FUNCTIONS
    
    # a function to encrypt keys
    # uses Fernet but supports arbitrary length 
    def _encrypt(self, value:str) -> bytes:
        
        # cast value to string
        # all keys are stored as strings for simplicity
        value = str(value)
        
        results = []
        for subvalue in[value[i:i+240] for i in range(0, len(value), 240)]:
            # encrypt
            subresult = str(self._f.encrypt(subvalue.encode()))[2:-1]
            # add to results
            results.append(subresult)
        
        # join with "+" (a non-url-safe character) 
        return ("+".join(results)).encode()
    
    # a function to decrypt keys
    # uses Fernet but supports arbitrary length   
    def _decrypt(self, value) -> str:
        
        # convert to string
        value = str(value)
        
        # strip bytes artifacts
        if type(value) == str and value.startswith("b'"):
            value = value[2:-1]
        
        results = []
        # split fernet into subvalues
        for subvalue in value.split("+"):
            # decrypt
            subresult = self._f.decrypt(subvalue.encode()).decode()
            # add to list
            results.append(subresult)
        # combine and return
        return "".join(results)
    
    # OVERRIDE FUNCTIONS
    
    # insert a row, casting all values to strings
    def __setitem__(self, key, value) -> None:
        self._execute(f"""
                      INSERT OR REPLACE INTO {self._table_name}
                      ("key", "value")
                      VALUES ("{str(key)}", "{self._encrypt(value)}")
                      """)
    
    # get a single value or all values
    def __getitem__(self, key):
        if key is all and self._use_all:
            # get all keys
            result = self._fetchall(f"SELECT * FROM {self._table_name}")
            
            # format results into a dictionary
            return dict(zip([i[0] for i in result], 
                            [self._decrypt(i[1]) for i in result]))
        else:
            # get a single key
            result = self._fetchall(f"""
                        SELECT * FROM {self._table_name}
                        WHERE (key = "{str(key)}")
                        """)
            if len(result) == 0:
                return None
            else:
                return self._decrypt(result[0][1])
    
    # delete single or all values
    def __delitem__(self, key):       
        if key is all and self._use_all:
            # clear all values
            self._execute(f"DROP TABLE IF EXISTS {self._table_name}")
            # recreate table
            self._create()
        else:
            # delete a single value
            self._execute(f"""
                         DELETE FROM {self._table_name}
                         WHERE key = "{key}" 
                         """)
    
    # return none for missing
    def __missing__(self, arg):
        return None

# executes if run as a standalone program
if __name__ == '__main__':
    pass
