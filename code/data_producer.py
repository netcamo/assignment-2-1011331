import pandas as pd
import pika
import json
import os
import time
import requests


tenants = { "tenants" :  [
    { "tenant_id": "tenant_1",
        'file_path': os.getcwd() + '/../data/client-staging-input-directory/tenant_1/listings/data_small.csv',
        'table_metadata': {
            "table_name": "listings",
            "primary_key": ["host_id", "id"],
            "schema": [
                {"field": "id", "type": "int"},
                {"field": "host_id", "type": "int"},
                {"field": "host_name", "type": "text"},
                {"field": "neighbourhood", "type": "text"},
                {"field": "latitude", "type": "float"},
                {"field": "longitude", "type": "float"},
                {"field": "room_type", "type": "text"},
                {"field": "price", "type": "int"},
                {"field": "availability_365", "type": "int"}
            ]
        }
    },

    { "tenant_id": "tenant_2",
        'file_path': os.getcwd() + '/../data/client-staging-input-directory/tenant_2/another_listing/data_small.csv',
        'table_metadata': {
            "table_name": "another_listing",
            "primary_key": ["host_id", "id"],
            "schema": [
                {"field": "id", "type": "int"},
                {"field": "host_id", "type": "int"},
                {"field": "host_name", "type": "text"},
                {"field": "neighbourhood", "type": "text"},
                {"field": "latitude", "type": "float"},
                {"field": "longitude", "type": "float"},
                {"field": "room_type", "type": "text"},
                {"field": "price", "type": "int"},
                {"field": "availability_365", "type": "int"}
            ]
        }
    }
 ] }


headers = {
    'content-type': 'application/json',
}
for tenant in tenants['tenants']:
    response = requests.put('http://localhost:15672/api/vhosts/{}'.format(tenant['tenant_id']), headers=headers, auth=('rbmq', 'rbmq'))

    
    CRENDENTIALS = pika.PlainCredentials('rbmq', 'rbmq')
    connection = pika.BlockingConnection(pika.ConnectionParameters(host="0.0.0.0", virtual_host=tenant['tenant_id'], credentials=CRENDENTIALS))
    channel = connection.channel()


    
    channel.exchange_declare(exchange='default', exchange_type='direct')

    
    table=tenant['table_metadata']
                
    result = channel.queue_declare(queue='', exclusive=True)

    
    queue_name = result.method.queue
         
    channel.queue_bind(exchange='default', queue=queue_name, routing_key=table['table_name'])

    reader = pd.read_csv(tenant['file_path'], chunksize=50)

    print("tenant new")
    count=0
    for chunk_df in reader:
        for row in chunk_df.itertuples():
            count+=1
            data = {
                item['field']: getattr(row, item['field']) if not pd.isna(getattr(row, item['field'])) else None for item in table['schema']
            }
            
            channel.basic_publish(exchange='default', routing_key=table['table_name'], body=json.dumps(data))
            print (data)
            
            
    print(count)

