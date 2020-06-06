# JSON2Obj

JSON2Obj allows you to read JSON, yaml, or dictionaries to Python objects.

## Features
- Read JSON and yaml files into Python objects.
- Store environment variable references in JSON or yaml config files.
  - **BONUS**: Environment variables can be stored encrypted, for example with AWS KMS.
- Seamlessly access stored information as if it was stored in a Python object.

## Use Cases
There are many use cases you can have for JSON2Obj. The main case that I created this for was making config
files for programs I wrote. This was a way to easily read user config files and store them as config
objects that I could then access later as the program was running.

I am sure that there are many other use cases for this as well.

---

# Installation
### Pypi & pip:

```bash
$> pip install json2obj
```

### From Source:
```bash
$> git clone https://github.com/zpriddy/JSON2Obj.git
$> cd JSON2Obj
$> python3 setup.py install
```

---

# Usage:
#### Example: Reading from JSON file
json file: `my_config.json`
```json
{
  "allow_access": true,
  "permissions": {
    "full_access": true,
    "edit": true
  },
  "custom": {
    "items": ["a", "b", "c"]
  }
}
```
application: `my_app.py`
```python
from JSON2Obj import read_json_file
config = read_json_file("my_config.json")

if config.allow_access:
    print("Allowing Access")
print(config.custom.items)
```

```bash
$> ./my_app.py
Allowing Access
["a", "b", "c"]
```

#### Example: Reading from yaml file
yaml file: `my_config.yaml`
```yaml
section1:
    allow_access: yes
    allow_guest: no
```
application: `my_app.py`
```python
from JSON2Obj import read_yaml_file
config = read_yaml_file("my_config.yaml")

if config.section1.allow_access:
    print("Allowing Access")
if config.section1.allow_guest:
    print("Allowing Guests")
```

```bash
$> ./my_app.py
Allowing Access
```

#### Example: Read from yaml with env vars
This is very useful if running an application in a Docker environment where things are set with environment variables. 

yaml file: `my_config.yaml`
```yaml
admin_settings:
    admin_username: admin
    admin_password: 
      env_var: ADMIN_PASSWORD
```

application: `my_app.py`
```python
from JSON2Obj import read_yaml_file
config = read_yaml_file("my_config.yaml")

if config.admin_settings:
    print(config.admin_settings.admin_username)
    print(config.admin_settings.admin_password)
```

```bash
$> export ADMIN_PASSWORD="MySecurePassword"
$>
$> ./my_app.py
admin
MySecurePassword
```

# Documentation
TODO: Link to read the docs