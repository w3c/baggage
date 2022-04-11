# Baggage Test Suite

---
**Note**

Test suite is not yet implemented.
This document describes the design of a test harness which will be implemented when the design is reviewed and approved.

---

This is a test harness built to test any baggage implementation and a reference baggage implementation written in Python.

- [Using the test suite](#using-the-test-suite)
  - [Requirements](#requirements)
    - [`parse`](#parse)
      - [Input](#input)
      - [Response](#response)
    - [`serialize`](#serialize)
      - [Input](#input-1)
- [Requirements](#requirements-1)

## Using the test suite

### Requirements

- Python 3.10+ <!-- TODO: determine minimum version -->
- A baggage implementation which implements the following endpoints

#### `parse`

Default path: `/baggage/parse`

This endpoint ensures that baggage is properly 

##### Input

This endpoint accepts an `HTTP GET` request with a `baggage` header

```http
GET /baggage/parse HTTP/1.1
Host: localhost
baggage: MyKey=MyValue;Property1;Property2=Property2Value
```

##### Response

A JSON list of parsed baggage entries in the following form.

```json
[
    {
        "key": "MyKey",
        "value": "MyValue",
        "properties": [
            {
                "key": "Property1"
            },
            {
                "key": "Property2",
                "value": "Property2Value"
            }
        ]
    }
]
```

#### `serialize`

Default path `/baggage/serialize`

##### Input



## Requirements

- MUST correctly parse 

