import sqlite3
import sys
import os

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
                 db_name = "keyway"):
        
        # set db name
        self._db_name = db_name
        
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

    
    # OVERRIDE FUNCTIONS
    
    # insert a row, casting all values to strings
    def __setitem__(self, key, value) -> None:
        self._execute(f"""
                      INSERT OR REPLACE INTO {self._table_name}
                      ("key", "value")
                      VALUES ("{str(key)}", "{str(value)}")
                      """)
    
    def __getitem__(self, key):
        if key is all:
            # get all keys
            result = self._fetchall(f"SELECT * FROM {self._table_name}")
            
            # format results into a dictionary
            return dict(zip([i[0] for i in result], 
                            [i[1] for i in result]))
        else:
            # get a single key
            result = self._fetchall(f"""
                        SELECT * FROM {self._table_name}
                        WHERE (key = "{str(key)}")
                        """)
            if len(result) == 0:
                return None
            else:
                return result[0][1]
    
    # delete
    def __delitem__(self, key):       
        if key is all:
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
