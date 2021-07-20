# ddbcereal
A high performance Python library for serializing and deserializing DynamoDB
attribute values.

Serializers and deserializers created with ddbcereal work with the input and
output of AWS SDKs like botocore, aiobotocore, and the low-level client
interfaces of boto3 and aioboto3.

This library endeavors to be at least as fast as boto3's (de)serializer and has
the option to work with inexact numbers like floats.

[Documentation](https://ddbcereal.readthedocs.io/)

## Usage
Create a `Serializer` for getting data into the native DynamoDB format:
* `serializer.serialize(value)` to serialize individual values
* `serializer.serialize_item(mapping)` to serialize an entire dict of values.
  
Create `Deserializer` for getting native DynamoDB data into native Python values:
* `deserializer.deserialize(value)` to deserialize individual values
* `deserializer.deserialize_item(mapping)` for complete items from the AWS SDK

## Example
```python
import aiobotocore
import ddbcereal

serializer = ddbcereal.Serializer()
deserializer = ddbcereal.Deserializer()

aws = aiobotocore.Session()

async with aws.create_client('dynamodb') as ddb:
    # Serialize entire dict as a DynamoDB item
    await ddb.put_item(
        TableName='MyItems',
        Item=serializer.serialize_item(my_dict)
    )

    # Serialize single values
    await ddb.update_item(
        TableName='Customers',
        Key={'id': serializer.serialize(customer_id)},
        UpdateExpression='SET displayName = :name, licenses = :licenses',
        ExpressionAttributeValues={
            ':name': serializer.serialize('ACME, Inc.'),
            ':licenses': serializer.serialize(20)
        }
    )

    # Deserializing:
    response = await ddb.query(
            TableName='Companies',
            KeyConditionExpression='id = :id',
            ExpressionAttributeValues={
                ':id': serializer.serialize(customer_id)
            }
        )
    companies = [
        deserializer.deserialize_item(item)
        for item in response.get('Items', ())
    ]
```
