Performance
===========
This library strives to be at least as fast as boto3's (de)serializer.

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
