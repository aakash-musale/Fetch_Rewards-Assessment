import boto3
from boto3.session import Session
import json
import psycopg2
import datetime
from psycopg2.extensions import AsIs, quote_ident
import os

# SQS queue URL
sqs_queue_url = 'http://localhost:4566/000000000000/login-queue'

# aws keys 
aws_region_name = os.environ.get('AWS_REGION_NAME','us-west-2')
aws_secret_access_key = os.environ.get('AWS_SECRET_ACCESS_KEY','x')
aws_access_key_id = os.environ.get('AWS_ACCESS_KEY_ID','x')

# postgres keys 
db_host = os.environ.get('DB_HOST','localhost')
db_name = os.environ.get('DB_NAME','postgres')
db_user = os.environ.get('POSTGRES_USER','postgres')
db_password = os.environ.get('POSTGRES_PASSWORD','postgres')

def postgres_connection():
    """
    Establishes a connection to the PostgreSQL database and returns the connection and cursor.
    """
    connection = psycopg2.connect(
        host=db_host,
        dbname=db_name,
        user=db_user,
        password=db_password
    )
    
    cursor = connection.cursor()
    return connection, cursor

def sqs_connection():
    """
    Creates an AWS SQS client and returns the client object.
    """
    session = boto3.Session()

    sqs_client = session.client('sqs',
                                endpoint_url=sqs_queue_url,
                                region_name=aws_region_name,
                                aws_secret_access_key=aws_secret_access_key,
                                aws_access_key_id=aws_access_key_id,
                                use_ssl=False)
    return sqs_client
    
def initialize_pii_dictionary():
    """
    Initializes and returns a dictionary for storing PII mappings.
    """
    return {
            "device_id": dict(),
            "ip": dict()
    }

def receive_sqs_message(client):
    """
    Receives a message from the SQS queue. 'client' is the SQS client connection.
    """
    return client.receive_message(
        QueueUrl=sqs_queue_url,
        MaxNumberOfMessages=1,
        VisibilityTimeout=60,
        WaitTimeSeconds=20
    )


if __name__ == "__main__":
    
    # Establish PostgreSQL connection
    connection, cursor = postgres_connection()
    # Establish SQS client connection
    sqs_client = sqs_connection()
    # Initialize PII dictionary
    pii_dict = initialize_pii_dictionary()
    messages = 1
    
    while messages:
        # Receive messages from SQS
        response = receive_sqs_message(sqs_client)
        # Get the messages
        messages = response.get('Messages')
        
        if messages is not None:
            for message in messages:
                # Extract message body
                message_body = message.get('Body')
                # Get receipt handle to delete message post processing
                receipt_handle = message.get('ReceiptHandle')
                # Parse JSON message
                json_message = json.loads(message_body)
                
                try:
                    hashed_ip = hash(json_message['ip'])
                    pii_dict['ip'][json_message['ip']] = hashed_ip
                    hashed_device_id = hash(json_message['device_id'])
                    pii_dict['device_id'][json_message['device_id']] = hashed_device_id
                    app_version = json_message['app_version'].split('.')[0]
                    
                    cursor.execute(f"""
                            INSERT INTO {AsIs(quote_ident('user_logins', cursor))}
                            VALUES ('{json_message['user_id']}','{json_message['device_type']}','{hashed_ip}','{hashed_device_id}','{json_message['locale']}','{app_version}','{datetime.datetime.utcnow()}');
                    """)
                    connection.commit()

                    # Delete message post processing
                    sqs_client.delete_message(
                        QueueUrl=sqs_queue_url,
                        ReceiptHandle=receipt_handle
                    )
                except KeyError:
                    print(f"Key Error on message {receipt_handle}")
                    sqs_client.delete_message(
                        QueueUrl=sqs_queue_url,
                        ReceiptHandle=receipt_handle
                    )
                    continue

    
    #printing db
    print('Final DB:')
    print("user_id,device_type,masked_ip,masked_device_id,locale,app_version,create_date")
    cursor.execute("SELECT * FROM user_logins")
    records = cursor.fetchall()
    print(records)
