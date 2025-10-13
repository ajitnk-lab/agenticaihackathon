import * as cdk from 'aws-cdk-lib';
import * as ec2 from 'aws-cdk-lib/aws-ec2';
import * as iam from 'aws-cdk-lib/aws-iam';
import * as dynamodb from 'aws-cdk-lib/aws-dynamodb';
import * as s3 from 'aws-cdk-lib/aws-s3';
import * as cloudfront from 'aws-cdk-lib/aws-cloudfront';
import * as origins from 'aws-cdk-lib/aws-cloudfront-origins';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as apigateway from 'aws-cdk-lib/aws-apigateway';
import { Construct } from 'constructs';

export class SecurityInfrastructureStack extends cdk.Stack {
  public readonly vpc: ec2.Vpc;
  public readonly securityFindingsTable: dynamodb.Table;
  public readonly reportsBucket: s3.Bucket;
  public readonly webBucket: s3.Bucket;
  public readonly distribution: cloudfront.Distribution;
  public readonly securityMcpFunction: lambda.Function;
  public readonly accountDiscoveryFunction: lambda.Function;

  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    // VPC with private subnets for secure deployment
    this.vpc = new ec2.Vpc(this, 'SecurityInfrastructureVpc', {
      maxAzs: 2,
      natGateways: 1,
      subnetConfiguration: [
        {
          cidrMask: 24,
          name: 'Public',
          subnetType: ec2.SubnetType.PUBLIC,
        },
        {
          cidrMask: 24,
          name: 'Private',
          subnetType: ec2.SubnetType.PRIVATE_WITH_EGRESS,
        },
      ],
    });

    // DynamoDB table for security findings
    this.securityFindingsTable = new dynamodb.Table(this, 'SecurityFindings', {
      tableName: 'security-orchestrator-findings',
      partitionKey: { name: 'accountId', type: dynamodb.AttributeType.STRING },
      sortKey: { name: 'findingId', type: dynamodb.AttributeType.STRING },
      billingMode: dynamodb.BillingMode.PAY_PER_REQUEST,
      encryption: dynamodb.TableEncryption.AWS_MANAGED,
      pointInTimeRecovery: true,
      removalPolicy: cdk.RemovalPolicy.DESTROY, // For hackathon - use RETAIN in production
    });

    // Add GSI for querying by severity
    this.securityFindingsTable.addGlobalSecondaryIndex({
      indexName: 'severity-index',
      partitionKey: { name: 'severity', type: dynamodb.AttributeType.STRING },
      sortKey: { name: 'createdAt', type: dynamodb.AttributeType.STRING },
    });

    // S3 bucket for reports
    this.reportsBucket = new s3.Bucket(this, 'ReportsBucket', {
      bucketName: `security-orchestrator-reports-${this.account}`,
      encryption: s3.BucketEncryption.S3_MANAGED,
      blockPublicAccess: s3.BlockPublicAccess.BLOCK_ALL,
      versioned: true,
      lifecycleRules: [
        {
          id: 'DeleteOldReports',
          expiration: cdk.Duration.days(90),
        },
      ],
      removalPolicy: cdk.RemovalPolicy.DESTROY, // For hackathon
    });

    // S3 bucket for web interface
    this.webBucket = new s3.Bucket(this, 'WebBucket', {
      bucketName: `security-orchestrator-web-${this.account}`,
      encryption: s3.BucketEncryption.S3_MANAGED,
      blockPublicAccess: s3.BlockPublicAccess.BLOCK_ALL,
      removalPolicy: cdk.RemovalPolicy.DESTROY, // For hackathon
    });

    // CloudFront distribution for web interface
    this.distribution = new cloudfront.Distribution(this, 'WebDistribution', {
      defaultBehavior: {
        origin: new origins.S3Origin(this.webBucket),
        viewerProtocolPolicy: cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
        cachePolicy: cloudfront.CachePolicy.CACHING_OPTIMIZED,
      },
      defaultRootObject: 'index.html',
      errorResponses: [
        {
          httpStatus: 404,
          responseHttpStatus: 200,
          responsePagePath: '/index.html',
        },
      ],
    });

    // IAM role for Lambda functions
    const lambdaExecutionRole = new iam.Role(this, 'LambdaExecutionRole', {
      assumedBy: new iam.ServicePrincipal('lambda.amazonaws.com'),
      managedPolicies: [
        iam.ManagedPolicy.fromAwsManagedPolicyName('service-role/AWSLambdaVPCExecutionRole'),
        iam.ManagedPolicy.fromAwsManagedPolicyName('SecurityAudit'),
      ],
      inlinePolicies: {
        SecurityAnalysisPolicy: new iam.PolicyDocument({
          statements: [
            new iam.PolicyStatement({
              effect: iam.Effect.ALLOW,
              actions: [
                'dynamodb:PutItem',
                'dynamodb:GetItem',
                'dynamodb:Query',
                'dynamodb:Scan',
                'dynamodb:UpdateItem',
                's3:GetObject',
                's3:PutObject',
                'organizations:ListAccounts',
                'organizations:DescribeOrganization',
                'ce:GetCostAndUsage',
                'ce:GetUsageReport',
              ],
              resources: [
                this.securityFindingsTable.tableArn,
                `${this.securityFindingsTable.tableArn}/index/*`,
                `${this.reportsBucket.bucketArn}/*`,
                '*', // For AWS security services
              ],
            }),
          ],
        }),
      },
    });

    // Lambda function for Well-Architected Security MCP Server
    this.securityMcpFunction = new lambda.Function(this, 'SecurityMcpFunction', {
      runtime: lambda.Runtime.PYTHON_3_10,
      handler: 'index.handler',
      code: lambda.Code.fromInline(`
import json
import boto3
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def handler(event, context):
    """
    Well-Architected Security MCP Server Lambda Handler
    Provides security analysis tools for multi-account environments
    """
    try:
        # Parse MCP request
        method = event.get('method', 'unknown')
        params = event.get('params', {})
        
        logger.info(f"Processing MCP request: {method}")
        
        if method == 'checkSecurityServices':
            return check_security_services(params)
        elif method == 'getSecurityFindings':
            return get_security_findings(params)
        elif method == 'analyzeSecurityPosture':
            return analyze_security_posture(params)
        elif method == 'exploreAwsResources':
            return explore_aws_resources(params)
        else:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': f'Unknown method: {method}'})
            }
            
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }

def check_security_services(params):
    """Check status of AWS security services"""
    account_id = params.get('accountId', 'current')
    
    # Initialize AWS clients
    guardduty = boto3.client('guardduty')
    securityhub = boto3.client('securityhub')
    inspector = boto3.client('inspector2')
    
    results = {
        'accountId': account_id,
        'services': {},
        'timestamp': context.aws_request_id if 'context' in globals() else 'test'
    }
    
    try:
        # Check GuardDuty
        detectors = guardduty.list_detectors()
        results['services']['guardduty'] = {
            'enabled': len(detectors['DetectorIds']) > 0,
            'detectors': len(detectors['DetectorIds'])
        }
    except Exception as e:
        results['services']['guardduty'] = {'enabled': False, 'error': str(e)}
    
    try:
        # Check Security Hub
        hub = securityhub.describe_hub()
        results['services']['securityhub'] = {
            'enabled': True,
            'hubArn': hub['HubArn']
        }
    except Exception as e:
        results['services']['securityhub'] = {'enabled': False, 'error': str(e)}
    
    try:
        # Check Inspector
        account = inspector.batch_get_account_status(accountIds=[account_id])
        results['services']['inspector'] = {
            'enabled': True,
            'status': account['accounts'][0]['state'] if account['accounts'] else 'unknown'
        }
    except Exception as e:
        results['services']['inspector'] = {'enabled': False, 'error': str(e)}
    
    return {
        'statusCode': 200,
        'body': json.dumps(results)
    }

def get_security_findings(params):
    """Get security findings from AWS services"""
    account_id = params.get('accountId', 'current')
    severity = params.get('severity', 'HIGH')
    
    securityhub = boto3.client('securityhub')
    
    try:
        findings = securityhub.get_findings(
            Filters={
                'SeverityLabel': [{'Value': severity, 'Comparison': 'EQUALS'}],
                'RecordState': [{'Value': 'ACTIVE', 'Comparison': 'EQUALS'}]
            },
            MaxResults=50
        )
        
        results = {
            'accountId': account_id,
            'severity': severity,
            'findingsCount': len(findings['Findings']),
            'findings': [
                {
                    'id': f['Id'],
                    'title': f['Title'],
                    'severity': f['Severity']['Label'],
                    'type': f['Types'][0] if f['Types'] else 'Unknown',
                    'resource': f['Resources'][0]['Id'] if f['Resources'] else 'Unknown'
                }
                for f in findings['Findings'][:10]  # Limit to 10 for demo
            ]
        }
        
        return {
            'statusCode': 200,
            'body': json.dumps(results)
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e), 'accountId': account_id})
        }

def analyze_security_posture(params):
    """Analyze overall security posture"""
    account_id = params.get('accountId', 'current')
    
    # This would integrate with the Well-Architected Security framework
    # For now, return a basic analysis
    
    results = {
        'accountId': account_id,
        'securityScore': 75,  # Mock score
        'pillars': {
            'identity_and_access_management': {'score': 80, 'findings': 3},
            'detective_controls': {'score': 70, 'findings': 5},
            'infrastructure_protection': {'score': 75, 'findings': 4},
            'data_protection': {'score': 85, 'findings': 2},
            'incident_response': {'score': 65, 'findings': 6}
        },
        'recommendations': [
            'Enable GuardDuty in all regions',
            'Configure Security Hub standards',
            'Review IAM policies for least privilege'
        ]
    }
    
    return {
        'statusCode': 200,
        'body': json.dumps(results)
    }

def explore_aws_resources(params):
    """Explore AWS resources for security analysis"""
    account_id = params.get('accountId', 'current')
    service = params.get('service', 'ec2')
    
    if service == 'ec2':
        ec2 = boto3.client('ec2')
        instances = ec2.describe_instances()
        
        resources = []
        for reservation in instances['Reservations']:
            for instance in reservation['Instances']:
                resources.append({
                    'id': instance['InstanceId'],
                    'type': 'EC2Instance',
                    'state': instance['State']['Name'],
                    'securityGroups': [sg['GroupId'] for sg in instance['SecurityGroups']]
                })
    else:
        resources = [{'message': f'Service {service} not implemented yet'}]
    
    return {
        'statusCode': 200,
        'body': json.dumps({
            'accountId': account_id,
            'service': service,
            'resourceCount': len(resources),
            'resources': resources[:10]  # Limit for demo
        })
    }
      `),
      role: lambdaExecutionRole,
      vpc: this.vpc,
      timeout: cdk.Duration.minutes(5),
      environment: {
        DYNAMODB_TABLE: this.securityFindingsTable.tableName,
        REPORTS_BUCKET: this.reportsBucket.bucketName,
      },
    });

    // Lambda function for Account Discovery MCP Server
    this.accountDiscoveryFunction = new lambda.Function(this, 'AccountDiscoveryFunction', {
      runtime: lambda.Runtime.PYTHON_3_10,
      handler: 'index.handler',
      code: lambda.Code.fromInline(`
import json
import boto3
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def handler(event, context):
    """
    Account Discovery MCP Server Lambda Handler
    Discovers AWS accounts in organization
    """
    try:
        method = event.get('method', 'unknown')
        params = event.get('params', {})
        
        logger.info(f"Processing Account Discovery request: {method}")
        
        if method == 'listOrganizationAccounts':
            return list_organization_accounts(params)
        elif method == 'getAccountMetadata':
            return get_account_metadata(params)
        else:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': f'Unknown method: {method}'})
            }
            
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }

def list_organization_accounts(params):
    """List all accounts in AWS Organization"""
    try:
        organizations = boto3.client('organizations')
        
        # Get organization info
        org = organizations.describe_organization()
        
        # List all accounts
        accounts = organizations.list_accounts()
        
        results = {
            'organizationId': org['Organization']['Id'],
            'masterAccountId': org['Organization']['MasterAccountId'],
            'accountCount': len(accounts['Accounts']),
            'accounts': [
                {
                    'id': acc['Id'],
                    'name': acc['Name'],
                    'email': acc['Email'],
                    'status': acc['Status'],
                    'joinedTimestamp': acc['JoinedTimestamp'].isoformat() if 'JoinedTimestamp' in acc else None
                }
                for acc in accounts['Accounts']
            ]
        }
        
        return {
            'statusCode': 200,
            'body': json.dumps(results, default=str)
        }
        
    except Exception as e:
        # If Organizations not configured, return single account
        sts = boto3.client('sts')
        identity = sts.get_caller_identity()
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'organizationId': None,
                'masterAccountId': identity['Account'],
                'accountCount': 1,
                'accounts': [
                    {
                        'id': identity['Account'],
                        'name': 'Current Account',
                        'email': 'unknown',
                        'status': 'ACTIVE',
                        'joinedTimestamp': None
                    }
                ],
                'note': 'Organizations not configured - showing current account only'
            })
        }

def get_account_metadata(params):
    """Get metadata for specific account"""
    account_id = params.get('accountId')
    
    if not account_id:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'accountId parameter required'})
        }
    
    # For now, return basic metadata
    # In production, this would gather more detailed account information
    
    results = {
        'accountId': account_id,
        'metadata': {
            'regions': ['us-east-1', 'us-west-2', 'eu-west-1'],  # Mock data
            'services': ['ec2', 'lambda', 's3', 'dynamodb'],
            'lastAnalyzed': None,
            'securityScore': None
        }
    }
    
    return {
        'statusCode': 200,
        'body': json.dumps(results)
    }
      `),
      role: lambdaExecutionRole,
      vpc: this.vpc,
      timeout: cdk.Duration.minutes(2),
    });

    // API Gateway for MCP servers
    const api = new apigateway.RestApi(this, 'SecurityMcpApi', {
      restApiName: 'Security MCP API',
      description: 'API Gateway for Security MCP Servers',
      defaultCorsPreflightOptions: {
        allowOrigins: apigateway.Cors.ALL_ORIGINS,
        allowMethods: apigateway.Cors.ALL_METHODS,
      },
    });

    // Security MCP endpoint
    const securityResource = api.root.addResource('security');
    securityResource.addMethod('POST', new apigateway.LambdaIntegration(this.securityMcpFunction));

    // Account Discovery endpoint
    const accountsResource = api.root.addResource('accounts');
    accountsResource.addMethod('POST', new apigateway.LambdaIntegration(this.accountDiscoveryFunction));

    // Cross-account IAM role for security analysis
    const crossAccountRole = new iam.Role(this, 'CrossAccountSecurityRole', {
      roleName: 'SecurityOrchestratorCrossAccountRole',
      assumedBy: new iam.ServicePrincipal('bedrock.amazonaws.com'),
      description: 'Role for cross-account security analysis',
      managedPolicies: [
        iam.ManagedPolicy.fromAwsManagedPolicyName('SecurityAudit'),
        iam.ManagedPolicy.fromAwsManagedPolicyName('ReadOnlyAccess'),
      ],
      inlinePolicies: {
        SecurityAnalysisPolicy: new iam.PolicyDocument({
          statements: [
            new iam.PolicyStatement({
              effect: iam.Effect.ALLOW,
              actions: [
                'organizations:ListAccounts',
                'organizations:DescribeOrganization',
                'organizations:ListOrganizationalUnitsForParent',
                'ce:GetCostAndUsage',
                'ce:GetUsageReport',
                'ce:GetReservationCoverage',
                'ce:GetReservationPurchaseRecommendation',
                'ce:GetReservationUtilization',
                'ce:GetSavingsPlansUtilization',
                'ce:ListCostCategoryDefinitions',
              ],
              resources: ['*'],
            }),
          ],
        }),
      },
    });

    // Outputs
    new cdk.CfnOutput(this, 'VpcId', {
      value: this.vpc.vpcId,
      description: 'VPC ID for Security Infrastructure',
    });

    new cdk.CfnOutput(this, 'SecurityFindingsTableName', {
      value: this.securityFindingsTable.tableName,
      description: 'DynamoDB table for security findings',
    });

    new cdk.CfnOutput(this, 'ReportsBucketName', {
      value: this.reportsBucket.bucketName,
      description: 'S3 bucket for security reports',
    });

    new cdk.CfnOutput(this, 'WebBucketName', {
      value: this.webBucket.bucketName,
      description: 'S3 bucket for web interface',
    });

    new cdk.CfnOutput(this, 'CloudFrontUrl', {
      value: `https://${this.distribution.distributionDomainName}`,
      description: 'CloudFront URL for web interface',
    });

    new cdk.CfnOutput(this, 'CrossAccountRoleArn', {
      value: crossAccountRole.roleArn,
      description: 'Cross-account role ARN for security analysis',
    });

    new cdk.CfnOutput(this, 'SecurityMcpApiUrl', {
      value: api.url,
      description: 'API Gateway URL for Security MCP servers',
    });

    new cdk.CfnOutput(this, 'SecurityMcpFunctionName', {
      value: this.securityMcpFunction.functionName,
      description: 'Lambda function for Security MCP server',
    });

    new cdk.CfnOutput(this, 'AccountDiscoveryFunctionName', {
      value: this.accountDiscoveryFunction.functionName,
      description: 'Lambda function for Account Discovery MCP server',
    });
  }
}
