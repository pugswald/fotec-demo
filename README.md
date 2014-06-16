fotec-demo
==========

Simple web service for the fotec demo.

## Exposed URLs

All failures return a json structure:
```
{ "error" : "Reason for failure" }
```

* GET /card
Query list of cards associated with a user.  Requires the following params:
device - Device ID for user
pin - Password for user

Returns a json structure:
{ data: [ {

* POST /pay
Attempt to create a transaction using the following form data:
device - Device ID for user
pin - Password for user
amount - Amount for transaction
merchant - Merchant


## Prerequisites for server

* Python - flask, passlib
* sqlite3

