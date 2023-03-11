# Keyway
### Persistent environment variables!
A simple solution to prevent accidentally uploading your api keys to github. Functions similarly to normal environment variables, except the keys and values persist through restarts without having to use Bash.

```python 
pip install keyway 
```

Import with
```python
import keyway
kw = keyway.Keyway()
```
Set, access, and delete keys like a dictionary.
```python
kw["alpha"] = "an api key"
kw["bravo"] = "a setting"
kw["charlie"] = 42

kw["alpha"]
#>> "an api key"

del kw["alpha"]
```

Missing keys return None.
```python
kw["alpha"]
#>> None
```

Keys are not stored in memory.
```python
kw.keys()
#>> dict_keys([])
```

To retrieve a dict of all of a user's keys, use the "all" keyword. All keys are stored as text for simplicity.
```python
kw[all]
#>> {'bravo': 'a variable', 'charlie': '42'}
```

To delete all of a user's keys, use the "all" keyword.
```python
del kw[all]
kw[all]
#>> {}
```

* By default, keys are stored in the active environment folder
  * Never upload your virtual environment to github. 
  * Optionally set a custom path and/or database name like:
    * ``` python
      kw = keyway.Keyway(path = "your/custom/path", db_name = "custom_name")
      ```
  * You can also optionally set a user for the keyway instance: 
    * ```python
      kw = keyway.Keyway(user = "username")
      ```
* Keyway has no dependencies outside of the standard library. 
* License: MIT
