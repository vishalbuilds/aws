import boto3
import uuid
import time
import json
import logging
import os
import yaml



dynamodb=boto3.client('dynamodb')
dynamodb_resource=boto3.resource('dynamodb')

def load_config():
    with open("config.yaml","r") as file:
        return yaml.safe_load(file)
    
def fetch_table_attribute(table_name, key_name, key_value):
    try:
        table = dynamodb_resource.table(table_name)
        response=table.get_item({key_name:key_value})
        return response.get('Item',None)
    except Exception as e:
        raise ValueError(f"Error fetching data from table: {table_name}: {str(e)}")

def get_table_name_yaml(attribute_name):
    config=load_config()
    table_name= config['dynamoDB_table_name'].get(f"{attribute_name}_table",None)
    if not table_name:
        raise ValueError(f"no table confugured for attributes: {attribute_name}")
    return table_name





def lambda_handler(event,context):
    try: 
        universal_table = get_table_name_yaml("universal")
        key=event['Details']['queue']['name']
        universal_table_data=fetch_table_attribute(universal_table,'key',key)
        if not universal_table_data:
            return{
                'statusCode':400,
                'body':json.dumps({'error':'universal table data not found' }),
                'headers':{'contact-type':'application/json'}
            }
        response_data={'key':key}
    except Exception as e:
        raise ValueError(f"Error fetching data from table: {universal_table}: {str(e)}")
