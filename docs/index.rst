ddbcereal
=========
Create a ``Serializer`` for getting data into the native DynamoDB format:

* ``serializer.serialize(value)`` to serialize individual values
* ``serializer.serialize_item(mapping)`` to serialize an entire dict of values.
  
Create ``Deserializer`` for getting native DynamoDB data into native Python values:

* ``deserializer.deserialize(value)`` to deserialize individual values
* ``deserializer.deserialize_item(mapping)`` for complete items from the AWS SDK

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
