Usage
=====

Installation
------------
ddbcereal is `hosted on PyPI <https://pypi.org/project/ddbcereal/>`_ so it's as
simple as using your favorite installer:

.. code-block:: bash

    python -m pip install ddbcereal

.. code-block:: bash

    poetry add ddbcereal

The package uses semantic versioning to indicate backwards
compatible changes to the API.

Communicating with DynamoDB
---------------------------
ddbcereal does not transport data to or from DynamoDB. It's up to you to
provide that layer. This is usually done with an AWS SDK or an HTTP
library.

AWS SDKs
^^^^^^^^

ddbcereal is known to work with these libraries:

* aiobotocore
* botocore
* aioboto3's low-level interface
* boto3's low-level interface

aiobotocore will be used for most examples in this documentation.

Raw HTTP API
^^^^^^^^^^^^

ddbcereal can also work directly with the
`DynamoDB HTTP API <https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/Programming.LowLevelAPI.html>`_.
Before and after JSON processing, dicts can be fed to
:py:class:`Serializer`\ s and :py:class:`Deserializer`\ s constructed with
``raw_transport=True``. 

Basic Usage
-----------
Create a :py:class:`Serializer` to process data into the native DynamoDB format:

* ``serializer.serialize(value)`` to serialize individual values
* ``serializer.serialize_item(mapping)`` to serialize an entire dict of values.
  
Create :py:class:`Deserializer` for getting DynamoDB data into native Python
values:

* ``deserializer.deserialize(value)`` to deserialize individual values
* ``deserializer.deserialize_item(mapping)`` for complete items from the AWS SDK

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

.. class:: Serializer(allow_inexact=False, \
                      validate_numbers=True, \
                      raw_transport=False, \
                      datetime_format=ddbcereal.ISO_8601, \
                      fraction_type=ddbcereal.NUMBER, \
                      empty_set_type=ddbcereal.NUMBER_SET)

   :param bool allow_inexact: Whether to allow numbers whose exact value can't
      be represented in DynamoDB or Python. DynamoDB's Number type stores exact
      numbers (fixed decimals). ``float``\ s are considered inexact by their nature
      and are only accepted with this option enabled.

   :param bool validate_numbers: Whether to check inputted numbers to determine
      if they're valid for storage in DynamoDB and whether or not they conform
      to the ``allow_inexact`` parameter.

      When enabled, attempts to serialize invalid numbers will result in a
      :py:exc:`ValueError` being raised. When disabled, serialization is
      faster, but mistakes might only be caught after the serialized value has
      been sent to DynamoDB.

   :param bool raw_transport: Indicates that values have not been
      pre-processed. For example, Base 64 strings have not been converted to
      bytes. Use this when using the AWS HTTP API without an AWS SDK.

   :param DateFormat datetime_format: Determines how Python
      :py:class:`~datetime.datetime`\ s should be serialized. Possible
      enumerations are available on the ddbcereal top level module and the
      :py:class:`~ddbcereal.DateFormat` enum.

   :param DynamoDBType fraction_type: Determines how Python
      :py:class:`~fractions.Fraction`\ s should be serialized. Must be
      :py:attr:`~ddbcereal.DynamoDBType.NUMBER` or
      :py:attr:`~ddbcereal.DynamoDBType.STRING`. Enumerations are available on
      the ddbcereal top level module and the
      :py:class:`~ddbcereal.DynamoDBType` enum. 

   :param DynamoDBType empty_set_type: When an empty set is serialized, make
      the set this DynamoDB type. Must be
      :py:attr:`~ddbcereal.DynamoDBType.NUMBER_SET`,
      :py:attr:`~ddbcereal.DynamoDBType.STRING_SET`, or
      :py:attr:`~ddbcereal.DynamoDBType.BINARY_SET`. Enumerations are available
      on the ddbcereal top level module and the
      :py:class:`~ddbcereal.DynamoDBType` enum.

.. autoclass:: ddbcereal.DateFormat
   :members:

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

.. class:: Deserializer(allow_inexact=False, \
                        raw_transport=False, \
                        number_type: PythonNumber = PythonNumber.DECIMAL_ONLY, \
                        null_value: Any = None, \
                        null_factory: Callable[[], Any] = None)

   :param bool allow_inexact: Whether to allow conversion to a Python number
      that won't exactly convey the value stored in DynamoDB (e.g. rounding of
      significant digits is required). Deserializing numbers to ``float``\ s is
      only possible when this is enabled.

   :param bool raw_transport: Indicates to deserialize values to be transported
      without additional processing. Bytes will be transported as Base 64
      strings. Use this when using the AWS HTTP API without an AWS SDK.

   :param PythonNumber python_number: Determines how DynamoDB Numbers should be
      serialized. Possible enumerations are available on the ddbcereal top
      level module and the :py:class:`PythonNumber` enum:

      .. autoclass:: ddbcereal.PythonNumber
         :members:

   :param python_null_value: The Python value to convert DynamoDB Nulls to.
      Defaults to :py:class:`None`. An immutable value is recommended. Ignored
      if ``python_null_factory`` is supplied.

   :param Callable[[], Any] python_null_factory: A function invoked for every
      DynamoDB Null value. The Null is converted to the return value of the
      function. ``python_null_value`` is ignored if this is supplied.

Going Beyond the Basic Types
^^^^^^^^^^^^^^^^^^^^^^^^^^^^
ddbcereal deserializers don't know the final shape you want your data to
conform to. They find appropriate Python types for the few types of data that
DynamoDB can store. If you want to deserialize values into more advanced types,
consider using a marshalling library like marshmallow or Pydantic.

They can take the dict produced by deserialize_item and create an objec based
on a schema, an object with fields of built-in types like dates, deques and of
custom types.

See
:py:meth:`marshmallow.Schema.load` and
`Pydantic Models - Helper Functions <https://pydantic-docs.helpmanual.io/usage/models/#helper-functions>`_.

Exceptions
----------
.. autoexception:: ddbcereal.NumberInexactError
  :show-inheritance:

.. autoexception:: ddbcereal.NumberNotAllowedError
  :show-inheritance:
