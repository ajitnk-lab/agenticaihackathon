#!/usr/bin/env python3
import zipfile

with open('dashboard_working.html', 'r') as f:
    html_content = f.read().replace('"', '\\"').replace('`', '\\`')

lambda_code = f'''import json

def lambda_handler(event, context):
    html = """{html_content}"""
    
    return {{
        'statusCode': 200,
        'headers': {{
            'Content-Type': 'text/html',
            'Access-Control-Allow-Origin': '*'
        }},
        'body': html
    }}
'''

with zipfile.ZipFile('dashboard_working.zip', 'w') as z:
    z.writestr('lambda_function.py', lambda_code)

print("✅ Created working dashboard")
