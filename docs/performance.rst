Performance
===========
This library strives to be at least as fast as boto3's (de)serializer. It
achieves high speeds by making most of the expensive/slow decisions during the
construction of the serializer or deserializer object, which is expected to
only happen once in the lifecycle of an application.

Squeezing More Performance
--------------------------
By default, time is spent on validating that data being supplied to a
serializer will be allowed by DynamoDB once serialized. Significantly faster
serialization is possible when not validating input before sending it to
DynamoDB.

.. code-block:: python

    import ddbcereal

    serialize_fast = ddbcereal.Serializer(
        validate_numbers=False,
        validate_strings=False
    ).serialize

    # DynamoDB won't allow these values: 
    serialize_fast("")
    serialize_fast(256879329952249291330123429991419420941210)
    # But we processed them very quickly!


Known Limitations
-----------------
ddbcereal is is faster than boto3 at serializing everything *except* for Number
Sets (e.g. `set[Decimal]`, `frozenset[int]`)


Benchmarks
----------
.. list-table:: Serializer Benchmarks (ddbcereal 1.0.0 cpython 3.9.4, 3.1 GHz
                Intel Core i7)
   :widths: 25 25 50
   :header-rows: 1

   * - Operation
     - Default Options Compared to boto3
     - ``validate_numbers=False``, ``validate_strings=False`` Compared to boto3 
   * - Construct a Serializer, default options
     - 60x Slower
     - 60x Slower
   * - Decimal to Number
     - 1.4x faster
     - 2.9x faster
   * - int to Number
     - 1.4x faster
     - 2.4x faster
   * - str to String
     - 3.6x faster
     - 3.7x faster
   * - Mixed number types Set to Number Set
     - 1.2x slower
     - 1.1x faster
   * - Set[str] to String Set
     - 3.9x faster
     - 3.9x faster
   * - List of mixed types to List
     - 3.1x faster
     - 4.1x faster
   * - dict of mixed types to Map
     - 3.6x faster
     - 4.6x faster
   * - dict of 2 levels to Map
     - 3.4x faster
     - 4.6x faster
