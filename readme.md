# Keyway
### Persistent environment variables!
A simple solution to prevent ever uploading your api keys to github. Functions similarly to normal environment variables, except the keys and values persist through restarts. No dependencies outside of the standard library.

```import keyway
kw = keyway.Keyway()```

Set, access, and delete keys like a dict.
```kw["alpha"] = "an api key"
kw["bravo"] = "a setting"
kw["charlie"] = 42```

```kw["alpha"]
>> "an api key"```

```del kw["alpha"]```

Missing keys return None.
```kw["alpha"]
>> None```

Keys are not stored in memory.
```kw.keys()
>> dict_keys([])```

To retrieve a dict of all of a user's keys, use the "all" keyword. All keys are stored as text for simplicity.
```kw[all]
>> {'bravo': 'a variable', 'charlie': '42'}```

To delete all of a user's keys, use the "all" keyword.
```del kw[all]
kw[all]
#>> {}```

* By default, keys are stored in the active environment folder
  * Never upload your virtual environment to github. 
  * Optionally set a custom path and/or database name like:
    * ```keyway = Keyway(path = "your/custom/path", db_name = "custom_name")```
  * You can also optionally set a user for the keyway instance: 
    * ```keyway = Keyway(user = "username")```
