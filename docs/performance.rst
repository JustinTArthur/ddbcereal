Performance
===========
This library endeavours to be at least as fast as boto3's (de)serializer. It
achieves high speed by making most of the slow decisions during the
construction of the serializer or deserializer object, which is expected to
happen once in the lifecycle of an application.

Squeezing More Performance
--------------------------
By default, time is spent validating that data being supplied to a serializer
will be allowed by DynamoDB once serialized. Significantly faster serialization
is possible when not validating input before sending it to DynamoDB.

.. code-block:: python

    import ddbcereal

    serialize_fast = ddbcereal.Serializer(
        validate_numbers=False
    ).serialize

    # DynamoDB won't allow this value: 
    serialize_fast(256879329952249291330123429991419420941210)
    # But we processed it very quickly!

Notice the method can be saved to a variable to avoid the object method attr
lookup every time ``serialize`` is called.

Known Limitations
-----------------
* Constructing a serializer or deserializer is slow. It should be done once and
  the serializer or deserializer should be reused.
* Map serialization and deserialization uses recursion in its current
  implementation, so deep Maps will use more memory and could take longer than
  expected to process. boto3's Map processing has this same issue.

Benchmarks
----------
.. list-table:: Serializer Benchmarks (ddbcereal 2.1.0 cpython 3.9.4, 3.1 GHz
                Intel Core i7)
   :widths: 25 25 50
   :header-rows: 1

   * - Operation
     - Default Options Compared to boto3
     - ``validate_numbers=False`` Compared to boto3 
   * - Construct a Serializer, default options
     - 60x Slower
     - 60x Slower
   * - Decimal to Number
     - 1.9x faster
     - 2.8x faster
   * - int to Number
     - 2x faster
     - 3x faster
   * - str to String
     - 3.6x faster
     - 3.6x faster
   * - Mixed number types Set to Number Set
     - 1.1x faster
     - 1.4x faster
   * - Set[str] to String Set
     - 4.2x faster
     - 4.2x faster
   * - List of mixed types to List
     - 3.4x faster
     - 4x faster
   * - dict of mixed types to Map
     - 4x faster
     - 4.6x faster
   * - dict of 2 levels to Map
     - 4x faster
     - 4.8x faster
