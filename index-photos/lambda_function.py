import json
import urllib.parse
import boto3
from requests_aws4auth import AWS4Auth
import requests
from datetime import datetime

print('Loading function')

s3 = boto3.client('s3')


def lambda_handler(event, context):
    print("Received event: " + json.dumps(event, indent=2))

    # Get the object from the event and show its content type
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')

    client=boto3.client('rekognition')
    response = client.detect_labels(Image={'S3Object':{'Bucket':bucket,'Name':key}},
        MaxLabels=10,MinConfidence=75)
    labels = []
    for label in response['Labels']:
        labels.append(label["Name"].lower())
    #print(labels)
    response = s3.head_object(Bucket=bucket,Key=key)
    metadata = response['Metadata']
    customLables = []
    if 'customlabels' in metadata:
        customLables = metadata["customlabels"]
        customLables = customLables.split(',')
        print(customLables)
    for i in range(len(customLables)):
        customLables[i] = customLables[i].lower()

    labels = labels + customLables
    time = datetime.now()
    #print(lables)
    json_data = {
        "objectKey": key, 
        "bucket": bucket,
        "createdTimestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "labels": labels
    }
    #json_data = json.dumps(json_data)
    #print(json_data)
    
    
    
    host = 'https://search-photos-7iq5s6l2rv5b5ctfb5byg2g5oa.us-east-1.es.amazonaws.com/' # For example, my-test-domain.us-east-1.es.amazonaws.com
    region = 'us-east-1' # e.g. us-west-1
    
    service = 'es'
    credentials = boto3.Session().get_credentials()
    path = 'test/_update/'+key
    awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, region, service, session_token=credentials.token)
    
    url = host + path
    
    # The JSON body to accompany the request (if necessary)
    payload = {
    "doc": json_data
    ,
    "doc_as_upsert": True
    }
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    
    
    r = requests.post(url, auth=awsauth, json=payload,headers=headers) # requests.get, post, and delete have similar syntax
    
    print(r.text)

    
    



