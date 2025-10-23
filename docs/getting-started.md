# Getting Started with TM1py

TM1py is a Python library for interacting with **IBM Planning Analytics / TM1** via the REST API.

---

## Requirements

- python (3.7 or higher)
- requests
- requests_negotiate_sspi
- TM1 11, TM1 12
- keyring

## Optional Requirements

- pandas

## Installation

TM1py only

```bash
pip install TM1py
```

Or TM1py with pandas dataframe support

```bash
pip install "tm1py[pandas]"
```

## Connect and print server name and version

```python
from TM1py import TM1Service

with TM1Service(
    address="localhost",
    port=12354,
    user="admin",
    password="apple",
    ssl=True
) as tm1:
    print("Server Name:", tm1.server.get_server_name())
    print("Version:", tm1.server.get_product_version())
```
