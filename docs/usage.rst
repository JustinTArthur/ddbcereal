Usage
=====

Communicating with DynamoDB
---------------------------
ddbcereal does not transport data to or from DynamoDB. It's up to you to
provide that layer. ddbcereal is known to work with these libraries:

* aiobotocore
* botocore
* aioboto3's low-level interface
* boto3's low-level interface

ddbcereal assumes that JSON parsing and conversion of Base 64 data to bytes is
handled already. All of the SDKs listed above do this.

aiobotocore will be used for most examples in this documentation.

Serialize Python Data for DynamoDB
----------------------------------
To prepare data for DynamoDB, construct a serializer object and use it to
serialize items and attribute values as needed.

.. code-block:: python

    import aiobotocore
    import ddbcereal
    
    # Usually done at module level:
    serializer = ddbcereal.Serializer()
    aws = aiobotocore.Session()
    
    async with aws.create_client('dynamodb') as ddb:
        # For a given dict:
        await ddb.put_item(
            TableName='MyItems',
            Item=serializer.serialize_item(my_dict)
        )
    
        # Adjust a single value:
        await ddb.update_item(
            TableName='Customers',
            Key={'id': serializer.serialize(customer_id)},
            UpdateExpression='SET displayName = :name, licenses = :licenses',
            ExpressionAttributeValues={
                ':name': serializer.serialize('ACME, Inc.'),
                ':licenses': serializer.serialize(20)
            }
        )

Serializer Options
^^^^^^^^^^^^^^^^^^
Serializers can be configured to handle data in different ways according to
your needs.

.. class:: Serializer(self, \
                      allow_inexact=False, \
                      nullify_empty_string=False, \
                      validate_numbers=True, \
                      validate_strings=True, \
                      datetime_format=ddbcereal.ISO_8601, \
                      fraction_type=ddbcereal.NUMBER)

   :param bool allow_inexact: Whether to allow numbers whose exact value can't
      be represented in DynamoDB or Python. DynamoDB's Number type stores exact
      numbers (fixed decimals). floats are considered inexact by their nature
      and are only accepted with this option enabled.

   :param bool nullify_empty_string: When enabled, converts any ``""`` s to nulls
      as a convenience. DynamoDB does not allow empty strings to be stored.

   :param bool validate_numbers: Whether to check inputted numbers to determine
      if they're valid for storage in DynamoDB and whether or not they conform
      to the ``allow_inexact`` parameter.

      When enabled, attempts to serialize invalid numbers will result in a
      ``ValueError`` being raised. When disabled, serialization is faster, but
      mistakes might only be caught after the serialized value has been sent
      to DynamoDB.

   :param bool validate_strings: Raises a ``StringNotAllowedError`` on attempts
      to serialize empty strings, which DynamoDB can't store. Disabling will
      result in faster serialization.

   :param DateFormat datetime_format: Determines how Python datetimes should be
      serialized. Possible enumerations are available on the ddbcereal top
      level module and the DateFormat enum:

      .. autoclass:: ddbcereal.DateFormat
         :members:

   :param DynamoDBType fraction_type: Determines how Python ``Fraction`` s should
      be serialized. Possible enumerations are available on the ddbcereal top
      level module and the DynamoDBType enum: 

      .. autoclass:: ddbcereal.DynamoDBType
         :members:
         :undoc-members:

Deserialize DynamoDB Data into Python
-------------------------------------
Construct a ``Deserializer`` object and use it to deserialize items or
attribute values as needed.

.. code-block:: python

    import aiobotocore
    import ddbcereal
    
    deserializer = ddbcereal.Deserializer()
    
    serializer = ddbcereal.Serializer()
    aws = aiobotocore.Session()
    
    async with aws.create_client('dynamodb') as ddb:
        response = await ddb.query(
            TableName='Companies',
            KeyConditionExpression='id = :id',
            ExpressionAttributeValues={
                ':id': serializer.serialize(target_id)
            }
        )
        companies = [
            deserializer.deserialize_item(item)
            for item in response.get('Items', ())
        ]
        process_companies(companies)

Deserializer Options
^^^^^^^^^^^^^^^^^^^^

.. class:: Deserializer(self, \
                        allow_inexact=False, \
                        number_type: PythonNumber = PythonNumber.DECIMAL_ONLY, \
                        null_value: Any = None, \
                        null_factory: Callable[[], Any] = None)

   :param bool allow_inexact: Whether to allow conversion to a Python number
      that won't exactly convey the value stored in DynamoDB (e.g. rounding of
      significant digits is required). Deserializing numbers to floats is only
      possible when this is enabled.

   :param PythonNumber python_number: Determines how DynamoDB Numbers should be
      serialized. Possible enumerations are available on the ddbcereal top
      level module and the PythonNumber enum:

      .. autoclass:: ddbcereal.PythonNumber
         :members:

   :param python_null_value: The Python value to convert DynamoDB Nulls to.
      Defaults to ``None``. An immutable value is recommended. Ignored if
      ``python_null_factory`` is supplied.

   :param Callable[[], Any] python_null_factory: A function invoked for every
      DynamoDB Null value. The Null is converted to the return value of the
      function. ``python_null_value`` is ignored if this is supplied.

Exceptions
----------
.. versionadded:: 1.1.0

.. autoexception:: ddbcereal.NumberInexactError
  :show-inheritance:

.. autoexception:: ddbcereal.NumberNotAllowedError
  :show-inheritance:

.. autoexception:: ddbcereal.StringNotAllowedError
  :show-inheritance:
