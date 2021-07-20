ddbcereal
=========
A high performance Python library for serializing and deserializing DynamoDB
attribute values.

Serializers and deserializers created with ddbcereal work with the input and
output of AWS SDKs like botocore, aiobotocore, and the low-level client
interfaces of boto3 and aioboto3.

This library endeavors to be at least as fast as boto3's (de)serializer and has
the option to work with inexact numbers like floats.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   usage
   performance
   changelog


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
