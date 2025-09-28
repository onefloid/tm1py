# Getting Started with TM1py

TM1py is a Python library for interacting with **IBM Planning Analytics / TM1** via the REST API.

---

## Installation

```bash
pip install TM1py
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
