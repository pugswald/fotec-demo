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
  * device - Device ID for user
  * pin - Password for user  
 Returns a json structure:
  ```
{ "data": [ 
  { 
    "bank" : "Bank Name",
    "id"   : int - this is the card_id,
    "last_four" : "Last four digits of card (string)",
    "name" : "User's name for card",
    "network" : "Name of card network"
  },
  ...
  ]
}
```

* POST /pay

 Attempt to create a transaction using the following form data:
 * device - Device ID for user
 * pin - Password for user
 * card_id - Card id to use, returned by /card
 * amount - Amount for transaction
 * merchant - Merchant  
Returns a json string:
  ```
{ "approval" : "Approval string" }
```
## Prerequisites for server

* Python - flask, passlib
* sqlite3

