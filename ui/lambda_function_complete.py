import json

def lambda_handler(event, context):
    # Read the complete HTML file
    with open('/var/task/dashboard_memory_trends.html', 'r') as f:
        html = f.read()
    
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'text/html',
            'Access-Control-Allow-Origin': '*'
        },
        'body': html
    }
