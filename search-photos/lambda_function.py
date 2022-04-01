import json
import urllib.parse
import boto3
from requests_aws4auth import AWS4Auth
import requests
from datetime import datetime
import inflect


def lambda_handler(event, context):
    
    
    host = 'https://search-photos-7iq5s6l2rv5b5ctfb5byg2g5oa.us-east-1.es.amazonaws.com/' # For example, my-test-domain.us-east-1.es.amazonaws.com
    region = 'us-east-1' # e.g. us-west-1
    #comment to check if CI/CD pipeline works end-to-end    
    service = 'es'
    credentials = boto3.Session().get_credentials()
    path = 'test/_search'
    awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, region, service, session_token=credentials.token)
    
    url = host + path
    query = event['queryStringParameters']['q']
    
    client = boto3.client('lex-runtime')
    # The JSON body to accompany the request (if necessary)
    response = client.post_text(botName='PhotoAlbum',
                                botAlias='photofinal',
                                userId='testuser',
                                inputText=query)
    #so this is what we recieve back from lex after passing along the input text
    print(response)
    #use lex to disambiguate the query if it cannot simply search on the entire
    #query which is naturally less precise
    p = inflect.engine()
    if('slots' in response):
        slots_from_lex = response['slots']
        keyone = slots_from_lex['keyone']
        keytwo = slots_from_lex['keytwo']
     
        
        if(keyone is not None):
            if(p.singular_noun(keyone) is not False):
                keyone = p.singular_noun(keyone)
            query = keyone
        if(keytwo is not None):
            if(p.singular_noun(keyone) is not False):
                keyone = p.singular_noun(keyone)
            if(p.singular_noun(keytwo) is not False):
                keytwo = p.singular_noun(keytwo)
            query = keyone +" "+ keytwo
    print("THE QUERY IS:" + query)
    payload = {
    "query": {
    "simple_query_string" : {
        "query": query,
        "fields": ["labels"]
        }
      }
    }
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    
    
    r = requests.post(url, auth=awsauth, json=payload,headers=headers) # requests.get, post, and delete have similar syntax
    hits = (json.loads(r.text))["hits"]["hits"]
    
    print(hits)
    print(r.text)
    #comment for demo 
    results = []
    for hit in hits:
        name = name = hit["_source"]["objectKey"]
        labels =  hit["_source"]["labels"]
        photo = {
            "url": "https://photo-album-backend.s3.amazonaws.com/"+name,
            "labels":labels
        }
        results.append(photo)
    body = {"results":results}

    """response = {
        "isBase64Encoded": False,
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token,Accept,x-amz-meta-customLabels',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,PUT,GET'
        },
        'body':body
    }
    print(response)
    return json.dumps(response)"""
    return {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token,Accept,x-amz-meta-customLabels',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,PUT,GET'
        },
        'body':json.dumps(body)
    }

    



