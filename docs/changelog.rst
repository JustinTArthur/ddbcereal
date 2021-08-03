Changelog
=========
Upcoming
--------
* Faster Binary (de)serialization in raw transport mode.

2.1.0
-----
* Empty Python set is now serialized to a configurable Set type.
* Faster serialization for Number Sets and Binary Sets.
* Behind the scenes, DynamoDBType enumerations are now ``str``\ s of
  their type symbol.

2.0.1
-----
* Fix exceptions from typing on pre-3.9 Python

2.0.0
-----
* Remove ``nullify_empty_string`` and ``validate_strings`` options. DynamoDB
  supports empty strings now and users could do this at a different layer.
* Fix :py:meth:`ddbcereal.Serialize.serialize_item`.
* Fixed typing issues.
* Publish exceptions.

1.0.0
-----
First release, feature parity with boto3 [de]serializers.
