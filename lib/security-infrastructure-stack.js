"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.SecurityInfrastructureStack = void 0;
const cdk = require("aws-cdk-lib");
const ec2 = require("aws-cdk-lib/aws-ec2");
const iam = require("aws-cdk-lib/aws-iam");
const dynamodb = require("aws-cdk-lib/aws-dynamodb");
const s3 = require("aws-cdk-lib/aws-s3");
const cloudfront = require("aws-cdk-lib/aws-cloudfront");
const origins = require("aws-cdk-lib/aws-cloudfront-origins");
const lambda = require("aws-cdk-lib/aws-lambda");
const apigateway = require("aws-cdk-lib/aws-apigateway");
const bedrock = require("aws-cdk-lib/aws-bedrock");
class SecurityInfrastructureStack extends cdk.Stack {
    constructor(scope, id, props) {
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
        // Bedrock Agent Role for Security Orchestrator
        this.agentRole = new iam.Role(this, 'BedrockAgentRole', {
            assumedBy: new iam.ServicePrincipal('bedrock.amazonaws.com'),
            managedPolicies: [
                iam.ManagedPolicy.fromAwsManagedPolicyName('SecurityAudit'),
                iam.ManagedPolicy.fromAwsManagedPolicyName('ReadOnlyAccess'),
            ],
            inlinePolicies: {
                BedrockAgentPolicy: new iam.PolicyDocument({
                    statements: [
                        new iam.PolicyStatement({
                            effect: iam.Effect.ALLOW,
                            actions: [
                                'bedrock:InvokeModel',
                                'bedrock:InvokeModelWithResponseStream',
                                'agentcore:*',
                                'dynamodb:PutItem',
                                'dynamodb:GetItem',
                                'dynamodb:Query',
                                's3:GetObject',
                                's3:PutObject',
                            ],
                            resources: [
                                'arn:aws:bedrock:*::foundation-model/anthropic.claude-3-5-sonnet-20241022-v2:0',
                                this.securityFindingsTable.tableArn,
                                `${this.reportsBucket.bucketArn}/*`,
                            ],
                        }),
                    ],
                }),
            },
        });
        // Deploy Well-Architected Security MCP to AgentCore
        const mcpServerBucket = new s3.Bucket(this, 'McpServerBucket', {
            bucketName: `security-mcp-server-${cdk.Aws.ACCOUNT_ID}-${cdk.Aws.REGION}`,
            encryption: s3.BucketEncryption.S3_MANAGED,
            blockPublicAccess: s3.BlockPublicAccess.BLOCK_ALL,
            removalPolicy: cdk.RemovalPolicy.DESTROY,
        });
        // Package and upload MCP server code
        const mcpServerAsset = lambda.Code.fromAsset('./mcp-servers', {
            bundling: {
                image: lambda.Runtime.PYTHON_3_10.bundlingImage,
                command: [
                    'bash', '-c',
                    'pip install -r pyproject.toml -t /asset-output && cp -r src/* /asset-output/'
                ],
            },
        });
        // Create Bedrock Agent for Security Orchestrator
        this.bedrockAgent = new bedrock.CfnAgent(this, 'SecurityOrchestratorAgent', {
            agentName: 'SecurityOrchestratorAgent',
            description: 'Multi-Account AWS Security Orchestrator Agent for hackathon',
            foundationModel: 'anthropic.claude-3-5-sonnet-20241022-v2:0',
            agentResourceRoleArn: this.agentRole.roleArn,
            instruction: `You are a Multi-Account AWS Security Orchestrator Agent. Your role is to:
1. Discover AWS accounts in an organization
2. Analyze security posture across multiple accounts
3. Correlate cross-account security risks
4. Provide cost-aware security recommendations
5. Generate executive reports

Use the available MCP tools to perform comprehensive security analysis and provide actionable insights.`,
            idleSessionTtlInSeconds: 1800,
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
        new cdk.CfnOutput(this, 'BedrockAgentId', {
            value: this.bedrockAgent.attrAgentId,
            description: 'Bedrock Agent ID for Security Orchestrator',
        });
        new cdk.CfnOutput(this, 'BedrockAgentArn', {
            value: this.bedrockAgent.attrAgentArn,
            description: 'Bedrock Agent ARN for Security Orchestrator',
        });
    }
}
exports.SecurityInfrastructureStack = SecurityInfrastructureStack;
//# sourceMappingURL=data:application/json;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoic2VjdXJpdHktaW5mcmFzdHJ1Y3R1cmUtc3RhY2suanMiLCJzb3VyY2VSb290IjoiIiwic291cmNlcyI6WyJzZWN1cml0eS1pbmZyYXN0cnVjdHVyZS1zdGFjay50cyJdLCJuYW1lcyI6W10sIm1hcHBpbmdzIjoiOzs7QUFBQSxtQ0FBbUM7QUFDbkMsMkNBQTJDO0FBQzNDLDJDQUEyQztBQUMzQyxxREFBcUQ7QUFDckQseUNBQXlDO0FBQ3pDLHlEQUF5RDtBQUN6RCw4REFBOEQ7QUFDOUQsaURBQWlEO0FBQ2pELHlEQUF5RDtBQUN6RCxtREFBbUQ7QUFHbkQsTUFBYSwyQkFBNEIsU0FBUSxHQUFHLENBQUMsS0FBSztJQVd4RCxZQUFZLEtBQWdCLEVBQUUsRUFBVSxFQUFFLEtBQXNCO1FBQzlELEtBQUssQ0FBQyxLQUFLLEVBQUUsRUFBRSxFQUFFLEtBQUssQ0FBQyxDQUFDO1FBRXhCLGlEQUFpRDtRQUNqRCxJQUFJLENBQUMsR0FBRyxHQUFHLElBQUksR0FBRyxDQUFDLEdBQUcsQ0FBQyxJQUFJLEVBQUUsMkJBQTJCLEVBQUU7WUFDeEQsTUFBTSxFQUFFLENBQUM7WUFDVCxXQUFXLEVBQUUsQ0FBQztZQUNkLG1CQUFtQixFQUFFO2dCQUNuQjtvQkFDRSxRQUFRLEVBQUUsRUFBRTtvQkFDWixJQUFJLEVBQUUsUUFBUTtvQkFDZCxVQUFVLEVBQUUsR0FBRyxDQUFDLFVBQVUsQ0FBQyxNQUFNO2lCQUNsQztnQkFDRDtvQkFDRSxRQUFRLEVBQUUsRUFBRTtvQkFDWixJQUFJLEVBQUUsU0FBUztvQkFDZixVQUFVLEVBQUUsR0FBRyxDQUFDLFVBQVUsQ0FBQyxtQkFBbUI7aUJBQy9DO2FBQ0Y7U0FDRixDQUFDLENBQUM7UUFFSCx1Q0FBdUM7UUFDdkMsSUFBSSxDQUFDLHFCQUFxQixHQUFHLElBQUksUUFBUSxDQUFDLEtBQUssQ0FBQyxJQUFJLEVBQUUsa0JBQWtCLEVBQUU7WUFDeEUsU0FBUyxFQUFFLGdDQUFnQztZQUMzQyxZQUFZLEVBQUUsRUFBRSxJQUFJLEVBQUUs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QVcsRUFBRSwwQ0FBMEM7U0FDeEQsQ0FBQyxDQUFDO1FBRUgsSUFBSSxHQUFHLENBQUMsU0FBUyxDQUFDLElBQUksRUFBRSx5QkFBeUIsRUFBRTtZQUNqRCxLQUFLLEVBQUUsSUFBSSxDQUFDLG1CQUFtQixDQUFDLFlBQVk7WUFDNUMsV0FBVyxFQUFFLHlDQUF5QztTQUN2RCxDQUFDLENBQUM7UUFFSCxJQUFJLEdBQUcsQ0FBQyxTQUFTLENBQUMsSUFBSSxFQUFFLDhCQUE4QixFQUFFO1lBQ3RELEtBQUssRUFBRSxJQUFJLENBQUMsd0JBQXdCLENBQUMsWUFBWTtZQUNqRCxXQUFXLEVBQUUsa0RBQWtEO1NBQ2hFLENBQUMsQ0FBQztRQUVILElBQUksR0FBRyxDQUFDLFNBQVMsQ0FBQyxJQUFJLEVBQUUsZ0JBQWdCLEVBQUU7WUFDeEMsS0FBSyxFQUFFLElBQUksQ0FBQyxZQUFZLENBQUMsV0FBVztZQUNwQyxXQUFXLEVBQUUsNENBQTRDO1NBQzFELENBQUMsQ0FBQztRQUVILElBQUksR0FBRyxDQUFDLFNBQVMsQ0FBQyxJQUFJLEVBQUUsaUJBQWlCLEVBQUU7WUFDekMsS0FBSyxFQUFFLElBQUksQ0FBQyxZQUFZLENBQUMsWUFBWTtZQUNyQyxXQUFXLEVBQUUsNkNBQTZDO1NBQzNELENBQUMsQ0FBQztJQUNMLENBQUM7Q0FDRjtBQS9uQkQsa0VBK25CQyIsInNvdXJjZXNDb250ZW50IjpbImltcG9ydCAqIGFzIGNkayBmcm9tICdhd3MtY2RrLWxpYic7XG5pbXBvcnQgKiBhcyBlYzIgZnJvbSAnYXdzLWNkay1saWIvYXdzLWVjMic7XG5pbXBvcnQgKiBhcyBpYW0gZnJvbSAnYXdzLWNkay1saWIvYXdzLWlhbSc7XG5pbXBvcnQgKiBhcyBkeW5hbW9kYiBmcm9tICdhd3MtY2RrLWxpYi9hd3MtZHluYW1vZGInO1xuaW1wb3J0ICogYXMgczMgZnJvbSAnYXdzLWNkay1saWIvYXdzLXMzJztcbmltcG9ydCAqIGFzIGNsb3VkZnJvbnQgZnJvbSAnYXdzLWNkay1saWIvYXdzLWNsb3VkZnJvbnQnO1xuaW1wb3J0ICogYXMgb3JpZ2lucyBmcm9tICdhd3MtY2RrLWxpYi9hd3MtY2xvdWRmcm9udC1vcmlnaW5zJztcbmltcG9ydCAqIGFzIGxhbWJkYSBmcm9tICdhd3MtY2RrLWxpYi9hd3MtbGFtYmRhJztcbmltcG9ydCAqIGFzIGFwaWdhdGV3YXkgZnJvbSAnYXdzLWNkay1saWIvYXdzLWFwaWdhdGV3YXknO1xuaW1wb3J0ICogYXMgYmVkcm9jayBmcm9tICdhd3MtY2RrLWxpYi9hd3MtYmVkcm9jayc7XG5pbXBvcnQgeyBDb25zdHJ1Y3QgfSBmcm9tICdjb25zdHJ1Y3RzJztcblxuZXhwb3J0IGNsYXNzIFNlY3VyaXR5SW5mcmFzdHJ1Y3R1cmVTdGFjayBleHRlbmRzIGNkay5TdGFjayB7XG4gIHB1YmxpYyByZWFkb25seSB2cGM6IGVjMi5WcGM7XG4gIHB1YmxpYyByZWFkb25seSBzZWN1cml0eUZpbmRpbmdzVGFibGU6IGR5bmFtb2RiLlRhYmxlO1xuICBwdWJsaWMgcmVhZG9ubHkgcmVwb3J0c0J1Y2tldDogczMuQnVja2V0O1xuICBwdWJsaWMgcmVhZG9ubHkgd2ViQnVja2V0OiBzMy5CdWNrZXQ7XG4gIHB1YmxpYyByZWFkb25seSBkaXN0cmlidXRpb246IGNsb3VkZnJvbnQuRGlzdHJpYnV0aW9uO1xuICBwdWJsaWMgcmVhZG9ubHkgc2VjdXJpdHlNY3BGdW5jdGlvbjogbGFtYmRhLkZ1bmN0aW9uO1xuICBwdWJsaWMgcmVhZG9ubHkgYWNjb3VudERpc2NvdmVyeUZ1bmN0aW9uOiBsYW1iZGEuRnVuY3Rpb247XG4gIHB1YmxpYyByZWFkb25seSBiZWRyb2NrQWdlbnQ6IGJlZHJvY2suQ2ZuQWdlbnQ7XG4gIHB1YmxpYyByZWFkb25seSBhZ2VudFJvbGU6IGlhbS5Sb2xlO1xuXG4gIGNvbnN0cnVjdG9yKHNjb3BlOiBDb25zdHJ1Y3QsIGlkOiBzdHJpbmcsIHByb3BzPzogY2RrLlN0YWNrUHJvcHMpIHtcbiAgICBzdXBlcihzY29wZSwgaWQsIHByb3BzKTtcblxuICAgIC8vIFZQQyB3aXRoIHByaXZhdGUgc3VibmV0cyBmb3Igc2VjdXJlIGRlcGxveW1lbnRcbiAgICB0aGlzLnZwYyA9IG5ldyBlYzIuVnBjKHRoaXMsICdTZWN1cml0eUluZnJhc3RydWN0dXJlVnBjJywge1xuICAgICAgbWF4QXpzOiAyLFxuICAgICAgbmF0R2F0ZXdheXM6IDEsXG4gICAgICBzdWJuZXRDb25maWd1cmF0aW9uOiBbXG4gICAgICAgIHtcbiAgICAgICAgICBjaWRyTWFzazogMjQsXG4gICAgICAgICAgbmFtZTogJ1B1YmxpYycsXG4gICAgICAgICAgc3VibmV0VHlwZTogZWMyLlN1Ym5ldFR5cGUuUFVCTElDLFxuICAgICAgICB9LFxuICAgICAgICB7XG4gICAgICAgICAgY2lkck1hc2s6IDI0LFxuICAgICAgICAgIG5hbWU6ICdQcml2YXRlJyxcbiAgICAgICAgICBzdWJuZXRUeXBlOiBlYzIuU3VibmV0VHlwZS5QUklWQVRFX1dJVEhfRUdSRVNTLFxuICAgICAgICB9LFxuICAgICAgXSxcbiAgICB9KTtcblxuICAgIC8vIER5bmFtb0RCIHRhYmxlIGZvciBzZWN1cml0eSBmaW5kaW5nc1xuICAgIHRoaXMuc2VjdXJpdHlGaW5kaW5nc1RhYmxlID0gbmV3IGR5bmFtb2RiLlRhYmxlKHRoaXMsICdTZWN1cml0eUZpbmRpbmdzJywge1xuICAgICAgdGFibGVOYW1lOiAnc2VjdXJpdHktb3JjaGVzdHJhdG9yLWZpbmRpbmdzJyxcbiAgICAgIHBhcnRpdGlvbktleTogeyBuYW1lOiAnYWNjb3VudElkJywgdHlwZTogZHluYW1vZGIuQXR0cmlidXRlVHlwZS5TVFJJTkcgfSxcbiAgICAgIHNvcnRLZXk6IHsgbmFtZTogJ2ZpbmRpbmdJZCcsIHR5cGU6IGR5bmFtb2RiLkF0dHJpYnV0ZVR5cGUuU1RSSU5HIH0sXG4gICAgICBiaWxsaW5nTW9kZTogZHluYW1vZGIuQmlsbGluZ01vZGUuUEFZX1BFUl9SRVFVRVNULFxuICAgICAgZW5jcnlwdGlvbjogZHluYW1vZGIuVGFibGVFbmNyeXB0aW9uLkFXU19NQU5BR0VELFxuICAgICAgcG9pbnRJblRpbWVSZWNvdmVyeTogdHJ1ZSxcbiAgICAgIHJlbW92YWxQb2xpY3k6IGNkay5SZW1vdmFsUG9saWN5LkRFU1RST1ksIC8vIEZvciBoYWNrYXRob24gLSB1c2UgUkVUQUlOIGluIHByb2R1Y3Rpb25cbiAgICB9KTtcblxuICAgIC8vIEFkZCBHU0kgZm9yIHF1ZXJ5aW5nIGJ5IHNldmVyaXR5XG4gICAgdGhpcy5zZWN1cml0eUZpbmRpbmdzVGFibGUuYWRkR2xvYmFsU2Vjb25kYXJ5SW5kZXgoe1xuICAgICAgaW5kZXhOYW1lOiAnc2V2ZXJpdHktaW5kZXgnLFxuICAgICAgcGFydGl0aW9uS2V5OiB7IG5hbWU6ICdzZXZlcml0eScsIHR5cGU6IGR5bmFtb2RiLkF0dHJpYnV0ZVR5cGUuU1RSSU5HIH0sXG4gICAgICBzb3J0S2V5OiB7IG5hbWU6ICdjcmVhdGVkQXQnLCB0eXBlOiBkeW5hbW9kYi5BdHRyaWJ1dGVUeXBlLlNUUklORyB9LFxuICAgIH0pO1xuXG4gICAgLy8gUzMgYnVja2V0IGZvciByZXBvcnRzXG4gICAgdGhpcy5yZXBvcnRzQnVja2V0ID0gbmV3IHMzLkJ1Y2tldCh0aGlzLCAnUmVwb3J0c0J1Y2tldCcsIHtcbiAgICAgIGJ1Y2tldE5hbWU6IGBzZWN1cml0eS1vcmNoZXN0cmF0b3ItcmVwb3J0cy0ke3RoaXMuYWNjb3VudH1gLFxuICAgICAgZW5jcnlwdGlvbjogczMuQnVja2V0RW5jcnlwdGlvbi5TM19NQU5BR0VELFxuICAgICAgYmxvY2tQdWJsaWNBY2Nlc3M6IHMzLkJsb2NrUHVibGljQWNjZXNzLkJMT0NLX0FMTCxcbiAgICAgIHZlcnNpb25lZDogdHJ1ZSxcbiAgICAgIGxpZmVjeWNsZVJ1bGVzOiBbXG4gICAgICAgIHtcbiAgICAgICAgICBpZDogJ0RlbGV0ZU9sZFJlcG9ydHMnLFxuICAgICAgICAgIGV4cGlyYXRpb246IGNkay5EdXJhdGlvbi5kYXlzKDkwKSxcbiAgICAgICAgfSxcbiAgICAgIF0sXG4gICAgICByZW1vdmFsUG9saWN5OiBjZGsuUmVtb3ZhbFBvbGljeS5ERVNUUk9ZLCAvLyBGb3IgaGFja2F0aG9uXG4gICAgfSk7XG5cbiAgICAvLyBTMyBidWNrZXQgZm9yIHdlYiBpbnRlcmZhY2VcbiAgICB0aGlzLndlYkJ1Y2tldCA9IG5ldyBzMy5CdWNrZXQodGhpcywgJ1dlYkJ1Y2tldCcsIHtcbiAgICAgIGJ1Y2tldE5hbWU6IGBzZWN1cml0eS1vcmNoZXN0cmF0b3Itd2ViLSR7dGhpcy5hY2NvdW50fWAsXG4gICAgICBlbmNyeXB0aW9uOiBzMy5CdWNrZXRFbmNyeXB0aW9uLlMzX01BTkFHRUQsXG4gICAgICBibG9ja1B1YmxpY0FjY2VzczogczMuQmxvY2tQdWJsaWNBY2Nlc3MuQkxPQ0tfQUxMLFxuICAgICAgcmVtb3ZhbFBvbGljeTogY2RrLlJlbW92YWxQb2xpY3kuREVTVFJPWSwgLy8gRm9yIGhhY2thdGhvblxuICAgIH0pO1xuXG4gICAgLy8gQ2xvdWRGcm9udCBkaXN0cmlidXRpb24gZm9yIHdlYiBpbnRlcmZhY2VcbiAgICB0aGlzLmRpc3RyaWJ1dGlvbiA9IG5ldyBjbG91ZGZyb250LkRpc3RyaWJ1dGlvbih0aGlzLCAnV2ViRGlzdHJpYnV0aW9uJywge1xuICAgICAgZGVmYXVsdEJlaGF2aW9yOiB7XG4gICAgICAgIG9yaWdpbjogbmV3IG9yaWdpbnMuUzNPcmlnaW4odGhpcy53ZWJCdWNrZXQpLFxuICAgICAgICB2aWV3ZXJQcm90b2NvbFBvbGljeTogY2xvdWRmcm9udC5WaWV3ZXJQcm90b2NvbFBvbGljeS5SRURJUkVDVF9UT19IVFRQUyxcbiAgICAgICAgY2FjaGVQb2xpY3k6IGNsb3VkZnJvbnQuQ2FjaGVQb2xpY3kuQ0FDSElOR19PUFRJTUlaRUQsXG4gICAgICB9LFxuICAgICAgZGVmYXVsdFJvb3RPYmplY3Q6ICdpbmRleC5odG1sJyxcbiAgICAgIGVycm9yUmVzcG9uc2VzOiBbXG4gICAgICAgIHtcbiAgICAgICAgICBodHRwU3RhdHVzOiA0MDQsXG4gICAgICAgICAgcmVzcG9uc2VIdHRwU3RhdHVzOiAyMDAsXG4gICAgICAgICAgcmVzcG9uc2VQYWdlUGF0aDogJy9pbmRleC5odG1sJyxcbiAgICAgICAgfSxcbiAgICAgIF0sXG4gICAgfSk7XG5cbiAgICAvLyBJQU0gcm9sZSBmb3IgTGFtYmRhIGZ1bmN0aW9uc1xuICAgIGNvbnN0IGxhbWJkYUV4ZWN1dGlvblJvbGUgPSBuZXcgaWFtLlJvbGUodGhpcywgJ0xhbWJkYUV4ZWN1dGlvblJvbGUnLCB7XG4gICAgICBhc3N1bWVkQnk6IG5ldyBpYW0uU2VydmljZVByaW5jaXBhbCgnbGFtYmRhLmFtYXpvbmF3cy5jb20nKSxcbiAgICAgIG1hbmFnZWRQb2xpY2llczogW1xuICAgICAgICBpYW0uTWFuYWdlZFBvbGljeS5mcm9tQXdzTWFuYWdlZFBvbGljeU5hbWUoJ3NlcnZpY2Utcm9sZS9BV1NMYW1iZGFWUENFeGVjdXRpb25Sb2xlJyksXG4gICAgICAgIGlhbS5NYW5hZ2VkUG9saWN5LmZyb21Bd3NNYW5hZ2VkUG9saWN5TmFtZSgnU2VjdXJpdHlBdWRpdCcpLFxuICAgICAgXSxcbiAgICAgIGlubGluZVBvbGljaWVzOiB7XG4gICAgICAgIFNlY3VyaXR5QW5hbHlzaXNQb2xpY3k6IG5ldyBpYW0uUG9saWN5RG9jdW1lbnQoe1xuICAgICAgICAgIHN0YXRlbWVudHM6IFtcbiAgICAgICAgICAgIG5ldyBpYW0uUG9saWN5U3RhdGVtZW50KHtcbiAgICAgICAgICAgICAgZWZmZWN0OiBpYW0uRWZmZWN0LkFMTE9XLFxuICAgICAgICAgICAgICBhY3Rpb25zOiBbXG4gICAgICAgICAgICAgICAgJ2R5bmFtb2RiOlB1dEl0ZW0nLFxuICAgICAgICAgICAgICAgICdkeW5hbW9kYjpHZXRJdGVtJyxcbiAgICAgICAgICAgICAgICAnZHluYW1vZGI6UXVlcnknLFxuICAgICAgICAgICAgICAgICdkeW5hbW9kYjpTY2FuJyxcbiAgICAgICAgICAgICAgICAnZHluYW1vZGI6VXBkYXRlSXRlbScsXG4gICAgICAgICAgICAgICAgJ3MzOkdldE9iamVjdCcsXG4gICAgICAgICAgICAgICAgJ3MzOlB1dE9iamVjdCcsXG4gICAgICAgICAgICAgICAgJ29yZ2FuaXphdGlvbnM6TGlzdEFjY291bnRzJyxcbiAgICAgICAgICAgICAgICAnb3JnYW5pemF0aW9uczpEZXNjcmliZU9yZ2FuaXphdGlvbicsXG4gICAgICAgICAgICAgICAgJ2NlOkdldENvc3RBbmRVc2FnZScsXG4gICAgICAgICAgICAgICAgJ2NlOkdldFVzYWdlUmVwb3J0JyxcbiAgICAgICAgICAgICAgXSxcbiAgICAgICAgICAgICAgcmVzb3VyY2VzOiBbXG4gICAgICAgICAgICAgICAgdGhpcy5zZWN1cml0eUZpbmRpbmdzVGFibGUudGFibGVBcm4sXG4gICAgICAgICAgICAgICAgYCR7dGhpcy5zZWN1cml0eUZpbmRpbmdzVGFibGUudGFibGVBcm59L2luZGV4LypgLFxuICAgICAgICAgICAgICAgIGAke3RoaXMucmVwb3J0c0J1Y2tldC5idWNrZXRBcm59LypgLFxuICAgICAgICAgICAgICAgICcqJywgLy8gRm9yIEFXUyBzZWN1cml0eSBzZXJ2aWNlc1xuICAgICAgICAgICAgICBdLFxuICAgICAgICAgICAgfSksXG4gICAgICAgICAgXSxcbiAgICAgICAgfSksXG4gICAgICB9LFxuICAgIH0pO1xuXG4gICAgLy8gTGFtYmRhIGZ1bmN0aW9uIGZvciBXZWxsLUFyY2hpdGVjdGVkIFNlY3VyaXR5IE1DUCBTZXJ2ZXJcbiAgICB0aGlzLnNlY3VyaXR5TWNwRnVuY3Rpb24gPSBuZXcgbGFtYmRhLkZ1bmN0aW9uKHRoaXMsICdTZWN1cml0eU1jcEZ1bmN0aW9uJywge1xuICAgICAgcnVudGltZTogbGFtYmRhLlJ1bnRpbWUuUFlUSE9OXzNfMTAsXG4gICAgICBoYW5kbGVyOiAnaW5kZXguaGFuZGxlcicsXG4gICAgICBjb2RlOiBsYW1iZGEuQ29kZS5mcm9tSW5saW5lKGBcbmltcG9ydCBqc29uXG5pbXBvcnQgYm90bzNcbmltcG9ydCBsb2dnaW5nXG5cbmxvZ2dlciA9IGxvZ2dpbmcuZ2V0TG9nZ2VyKClcbmxvZ2dlci5zZXRMZXZlbChsb2dnaW5nLklORk8pXG5cbmRlZiBoYW5kbGVyKGV2ZW50LCBjb250ZXh0KTpcbiAgICBcIlwiXCJcbiAgICBXZWxsLUFyY2hpdGVjdGVkIFNlY3VyaXR5IE1DUCBTZXJ2ZXIgTGFtYmRhIEhhbmRsZXJcbiAgICBQcm92aWRlcyBzZWN1cml0eSBhbmFseXNpcyB0b29scyBmb3IgbXVsdGktYWNjb3VudCBlbnZpcm9ubWVudHNcbiAgICBcIlwiXCJcbiAgICB0cnk6XG4gICAgICAgICMgUGFyc2UgTUNQIHJlcXVlc3RcbiAgICAgICAgbWV0aG9kID0gZXZlbnQuZ2V0KCdtZXRob2QnLCAndW5rbm93bicpXG4gICAgICAgIHBhcmFtcyA9IGV2ZW50LmdldCgncGFyYW1zJywge30pXG4gICAgICAgIFxuICAgICAgICBsb2dnZXIuaW5mbyhmXCJQcm9jZXNzaW5nIE1DUCByZXF1ZXN0OiB7bWV0aG9kfVwiKVxuICAgICAgICBcbiAgICAgICAgaWYgbWV0aG9kID09ICdjaGVja1NlY3VyaXR5U2VydmljZXMnOlxuICAgICAgICAgICAgcmV0dXJuIGNoZWNrX3NlY3VyaXR5X3NlcnZpY2VzKHBhcmFtcylcbiAgICAgICAgZWxpZiBtZXRob2QgPT0gJ2dldFNlY3VyaXR5RmluZGluZ3MnOlxuICAgICAgICAgICAgcmV0dXJuIGdldF9zZWN1cml0eV9maW5kaW5ncyhwYXJhbXMpXG4gICAgICAgIGVsaWYgbWV0aG9kID09ICdhbmFseXplU2VjdXJpdHlQb3N0dXJlJzpcbiAgICAgICAgICAgIHJldHVybiBhbmFseXplX3NlY3VyaXR5X3Bvc3R1cmUocGFyYW1zKVxuICAgICAgICBlbGlmIG1ldGhvZCA9PSAnZXhwbG9yZUF3c1Jlc291cmNlcyc6XG4gICAgICAgICAgICByZXR1cm4gZXhwbG9yZV9hd3NfcmVzb3VyY2VzKHBhcmFtcylcbiAgICAgICAgZWxzZTpcbiAgICAgICAgICAgIHJldHVybiB7XG4gICAgICAgICAgICAgICAgJ3N0YXR1c0NvZGUnOiA0MDAsXG4gICAgICAgICAgICAgICAgJ2JvZHknOiBqc29uLmR1bXBzKHsnZXJyb3InOiBmJ1Vua25vd24gbWV0aG9kOiB7bWV0aG9kfSd9KVxuICAgICAgICAgICAgfVxuICAgICAgICAgICAgXG4gICAgZXhjZXB0IEV4Y2VwdGlvbiBhcyBlOlxuICAgICAgICBsb2dnZXIuZXJyb3IoZlwiRXJyb3IgcHJvY2Vzc2luZyByZXF1ZXN0OiB7c3RyKGUpfVwiKVxuICAgICAgICByZXR1cm4ge1xuICAgICAgICAgICAgJ3N0YXR1c0NvZGUnOiA1MDAsXG4gICAgICAgICAgICAnYm9keSc6IGpzb24uZHVtcHMoeydlcnJvcic6IHN0cihlKX0pXG4gICAgICAgIH1cblxuZGVmIGNoZWNrX3NlY3VyaXR5X3NlcnZpY2VzKHBhcmFtcyk6XG4gICAgXCJcIlwiQ2hlY2sgc3RhdHVzIG9mIEFXUyBzZWN1cml0eSBzZXJ2aWNlc1wiXCJcIlxuICAgIGFjY291bnRfaWQgPSBwYXJhbXMuZ2V0KCdhY2NvdW50SWQnLCAnY3VycmVudCcpXG4gICAgXG4gICAgIyBJbml0aWFsaXplIEFXUyBjbGllbnRzXG4gICAgZ3VhcmRkdXR5ID0gYm90bzMuY2xpZW50KCdndWFyZGR1dHknKVxuICAgIHNlY3VyaXR5aHViID0gYm90bzMuY2xpZW50KCdzZWN1cml0eWh1YicpXG4gICAgaW5zcGVjdG9yID0gYm90bzMuY2xpZW50KCdpbnNwZWN0b3IyJylcbiAgICBcbiAgICByZXN1bHRzID0ge1xuICAgICAgICAnYWNjb3VudElkJzogYWNjb3VudF9pZCxcbiAgICAgICAgJ3NlcnZpY2VzJzoge30sXG4gICAgICAgICd0aW1lc3RhbXAnOiBjb250ZXh0LmF3c19yZXF1ZXN0X2lkIGlmICdjb250ZXh0JyBpbiBnbG9iYWxzKCkgZWxzZSAndGVzdCdcbiAgICB9XG4gICAgXG4gICAgdHJ5OlxuICAgICAgICAjIENoZWNrIEd1YXJkRHV0eVxuICAgICAgICBkZXRlY3RvcnMgPSBndWFyZGR1dHkubGlzdF9kZXRlY3RvcnMoKVxuICAgICAgICByZXN1bHRzWydzZXJ2aWNlcyddWydndWFyZGR1dHknXSA9IHtcbiAgICAgICAgICAgICdlbmFibGVkJzogbGVuKGRldGVjdG9yc1snRGV0ZWN0b3JJZHMnXSkgPiAwLFxuICAgICAgICAgICAgJ2RldGVjdG9ycyc6IGxlbihkZXRlY3RvcnNbJ0RldGVjdG9ySWRzJ10pXG4gICAgICAgIH1cbiAgICBleGNlcHQgRXhjZXB0aW9uIGFzIGU6XG4gICAgICAgIHJlc3VsdHNbJ3NlcnZpY2VzJ11bJ2d1YXJkZHV0eSddID0geydlbmFibGVkJzogRmFsc2UsICdlcnJvcic6IHN0cihlKX1cbiAgICBcbiAgICB0cnk6XG4gICAgICAgICMgQ2hlY2sgU2VjdXJpdHkgSHViXG4gICAgICAgIGh1YiA9IHNlY3VyaXR5aHViLmRlc2NyaWJlX2h1YigpXG4gICAgICAgIHJlc3VsdHNbJ3NlcnZpY2VzJ11bJ3NlY3VyaXR5aHViJ10gPSB7XG4gICAgICAgICAgICAnZW5hYmxlZCc6IFRydWUsXG4gICAgICAgICAgICAnaHViQXJuJzogaHViWydIdWJBcm4nXVxuICAgICAgICB9XG4gICAgZXhjZXB0IEV4Y2VwdGlvbiBhcyBlOlxuICAgICAgICByZXN1bHRzWydzZXJ2aWNlcyddWydzZWN1cml0eWh1YiddID0geydlbmFibGVkJzogRmFsc2UsICdlcnJvcic6IHN0cihlKX1cbiAgICBcbiAgICB0cnk6XG4gICAgICAgICMgQ2hlY2sgSW5zcGVjdG9yXG4gICAgICAgIGFjY291bnQgPSBpbnNwZWN0b3IuYmF0Y2hfZ2V0X2FjY291bnRfc3RhdHVzKGFjY291bnRJZHM9W2FjY291bnRfaWRdKVxuICAgICAgICByZXN1bHRzWydzZXJ2aWNlcyddWydpbnNwZWN0b3InXSA9IHtcbiAgICAgICAgICAgICdlbmFibGVkJzogVHJ1ZSxcbiAgICAgICAgICAgICdzdGF0dXMnOiBhY2NvdW50WydhY2NvdW50cyddWzBdWydzdGF0ZSddIGlmIGFjY291bnRbJ2FjY291bnRzJ10gZWxzZSAndW5rbm93bidcbiAgICAgICAgfVxuICAgIGV4Y2VwdCBFeGNlcHRpb24gYXMgZTpcbiAgICAgICAgcmVzdWx0c1snc2VydmljZXMnXVsnaW5zcGVjdG9yJ10gPSB7J2VuYWJsZWQnOiBGYWxzZSwgJ2Vycm9yJzogc3RyKGUpfVxuICAgIFxuICAgIHJldHVybiB7XG4gICAgICAgICdzdGF0dXNDb2RlJzogMjAwLFxuICAgICAgICAnYm9keSc6IGpzb24uZHVtcHMocmVzdWx0cylcbiAgICB9XG5cbmRlZiBnZXRfc2VjdXJpdHlfZmluZGluZ3MocGFyYW1zKTpcbiAgICBcIlwiXCJHZXQgc2VjdXJpdHkgZmluZGluZ3MgZnJvbSBBV1Mgc2VydmljZXNcIlwiXCJcbiAgICBhY2NvdW50X2lkID0gcGFyYW1zLmdldCgnYWNjb3VudElkJywgJ2N1cnJlbnQnKVxuICAgIHNldmVyaXR5ID0gcGFyYW1zLmdldCgnc2V2ZXJpdHknLCAnSElHSCcpXG4gICAgXG4gICAgc2VjdXJpdHlodWIgPSBib3RvMy5jbGllbnQoJ3NlY3VyaXR5aHViJylcbiAgICBcbiAgICB0cnk6XG4gICAgICAgIGZpbmRpbmdzID0gc2VjdXJpdHlodWIuZ2V0X2ZpbmRpbmdzKFxuICAgICAgICAgICAgRmlsdGVycz17XG4gICAgICAgICAgICAgICAgJ1NldmVyaXR5TGFiZWwnOiBbeydWYWx1ZSc6IHNldmVyaXR5LCAnQ29tcGFyaXNvbic6ICdFUVVBTFMnfV0sXG4gICAgICAgICAgICAgICAgJ1JlY29yZFN0YXRlJzogW3snVmFsdWUnOiAnQUNUSVZFJywgJ0NvbXBhcmlzb24nOiAnRVFVQUxTJ31dXG4gICAgICAgICAgICB9LFxuICAgICAgICAgICAgTWF4UmVzdWx0cz01MFxuICAgICAgICApXG4gICAgICAgIFxuICAgICAgICByZXN1bHRzID0ge1xuICAgICAgICAgICAgJ2FjY291bnRJZCc6IGFjY291bnRfaWQsXG4gICAgICAgICAgICAnc2V2ZXJpdHknOiBzZXZlcml0eSxcbiAgICAgICAgICAgICdmaW5kaW5nc0NvdW50JzogbGVuKGZpbmRpbmdzWydGaW5kaW5ncyddKSxcbiAgICAgICAgICAgICdmaW5kaW5ncyc6IFtcbiAgICAgICAgICAgICAgICB7XG4gICAgICAgICAgICAgICAgICAgICdpZCc6IGZbJ0lkJ10sXG4gICAgICAgICAgICAgICAgICAgICd0aXRsZSc6IGZbJ1RpdGxlJ10sXG4gICAgICAgICAgICAgICAgICAgICdzZXZlcml0eSc6IGZbJ1NldmVyaXR5J11bJ0xhYmVsJ10sXG4gICAgICAgICAgICAgICAgICAgICd0eXBlJzogZlsnVHlwZXMnXVswXSBpZiBmWydUeXBlcyddIGVsc2UgJ1Vua25vd24nLFxuICAgICAgICAgICAgICAgICAgICAncmVzb3VyY2UnOiBmWydSZXNvdXJjZXMnXVswXVsnSWQnXSBpZiBmWydSZXNvdXJjZXMnXSBlbHNlICdVbmtub3duJ1xuICAgICAgICAgICAgICAgIH1cbiAgICAgICAgICAgICAgICBmb3IgZiBpbiBmaW5kaW5nc1snRmluZGluZ3MnXVs6MTBdICAjIExpbWl0IHRvIDEwIGZvciBkZW1vXG4gICAgICAgICAgICBdXG4gICAgICAgIH1cbiAgICAgICAgXG4gICAgICAgIHJldHVybiB7XG4gICAgICAgICAgICAnc3RhdHVzQ29kZSc6IDIwMCxcbiAgICAgICAgICAgICdib2R5JzoganNvbi5kdW1wcyhyZXN1bHRzKVxuICAgICAgICB9XG4gICAgICAgIFxuICAgIGV4Y2VwdCBFeGNlcHRpb24gYXMgZTpcbiAgICAgICAgcmV0dXJuIHtcbiAgICAgICAgICAgICdzdGF0dXNDb2RlJzogNTAwLFxuICAgICAgICAgICAgJ2JvZHknOiBqc29uLmR1bXBzKHsnZXJyb3InOiBzdHIoZSksICdhY2NvdW50SWQnOiBhY2NvdW50X2lkfSlcbiAgICAgICAgfVxuXG5kZWYgYW5hbHl6ZV9zZWN1cml0eV9wb3N0dXJlKHBhcmFtcyk6XG4gICAgXCJcIlwiQW5hbHl6ZSBvdmVyYWxsIHNlY3VyaXR5IHBvc3R1cmVcIlwiXCJcbiAgICBhY2NvdW50X2lkID0gcGFyYW1zLmdldCgnYWNjb3VudElkJywgJ2N1cnJlbnQnKVxuICAgIFxuICAgICMgVGhpcyB3b3VsZCBpbnRlZ3JhdGUgd2l0aCB0aGUgV2VsbC1BcmNoaXRlY3RlZCBTZWN1cml0eSBmcmFtZXdvcmtcbiAgICAjIEZvciBub3csIHJldHVybiBhIGJhc2ljIGFuYWx5c2lzXG4gICAgXG4gICAgcmVzdWx0cyA9IHtcbiAgICAgICAgJ2FjY291bnRJZCc6IGFjY291bnRfaWQsXG4gICAgICAgICdzZWN1cml0eVNjb3JlJzogNzUsICAjIE1vY2sgc2NvcmVcbiAgICAgICAgJ3BpbGxhcnMnOiB7XG4gICAgICAgICAgICAnaWRlbnRpdHlfYW5kX2FjY2Vzc19tYW5hZ2VtZW50JzogeydzY29yZSc6IDgwLCAnZmluZGluZ3MnOiAzfSxcbiAgICAgICAgICAgICdkZXRlY3RpdmVfY29udHJvbHMnOiB7J3Njb3JlJzogNzAsICdmaW5kaW5ncyc6IDV9LFxuICAgICAgICAgICAgJ2luZnJhc3RydWN0dXJlX3Byb3RlY3Rpb24nOiB7J3Njb3JlJzogNzUsICdmaW5kaW5ncyc6IDR9LFxuICAgICAgICAgICAgJ2RhdGFfcHJvdGVjdGlvbic6IHsnc2NvcmUnOiA4NSwgJ2ZpbmRpbmdzJzogMn0sXG4gICAgICAgICAgICAnaW5jaWRlbnRfcmVzcG9uc2UnOiB7J3Njb3JlJzogNjUsICdmaW5kaW5ncyc6IDZ9XG4gICAgICAgIH0sXG4gICAgICAgICdyZWNvbW1lbmRhdGlvbnMnOiBbXG4gICAgICAgICAgICAnRW5hYmxlIEd1YXJkRHV0eSBpbiBhbGwgcmVnaW9ucycsXG4gICAgICAgICAgICAnQ29uZmlndXJlIFNlY3VyaXR5IEh1YiBzdGFuZGFyZHMnLFxuICAgICAgICAgICAgJ1JldmlldyBJQU0gcG9saWNpZXMgZm9yIGxlYXN0IHByaXZpbGVnZSdcbiAgICAgICAgXVxuICAgIH1cbiAgICBcbiAgICByZXR1cm4ge1xuICAgICAgICAnc3RhdHVzQ29kZSc6IDIwMCxcbiAgICAgICAgJ2JvZHknOiBqc29uLmR1bXBzKHJlc3VsdHMpXG4gICAgfVxuXG5kZWYgZXhwbG9yZV9hd3NfcmVzb3VyY2VzKHBhcmFtcyk6XG4gICAgXCJcIlwiRXhwbG9yZSBBV1MgcmVzb3VyY2VzIGZvciBzZWN1cml0eSBhbmFseXNpc1wiXCJcIlxuICAgIGFjY291bnRfaWQgPSBwYXJhbXMuZ2V0KCdhY2NvdW50SWQnLCAnY3VycmVudCcpXG4gICAgc2VydmljZSA9IHBhcmFtcy5nZXQoJ3NlcnZpY2UnLCAnZWMyJylcbiAgICBcbiAgICBpZiBzZXJ2aWNlID09ICdlYzInOlxuICAgICAgICBlYzIgPSBib3RvMy5jbGllbnQoJ2VjMicpXG4gICAgICAgIGluc3RhbmNlcyA9IGVjMi5kZXNjcmliZV9pbnN0YW5jZXMoKVxuICAgICAgICBcbiAgICAgICAgcmVzb3VyY2VzID0gW11cbiAgICAgICAgZm9yIHJlc2VydmF0aW9uIGluIGluc3RhbmNlc1snUmVzZXJ2YXRpb25zJ106XG4gICAgICAgICAgICBmb3IgaW5zdGFuY2UgaW4gcmVzZXJ2YXRpb25bJ0luc3RhbmNlcyddOlxuICAgICAgICAgICAgICAgIHJlc291cmNlcy5hcHBlbmQoe1xuICAgICAgICAgICAgICAgICAgICAnaWQnOiBpbnN0YW5jZVsnSW5zdGFuY2VJZCddLFxuICAgICAgICAgICAgICAgICAgICAndHlwZSc6ICdFQzJJbnN0YW5jZScsXG4gICAgICAgICAgICAgICAgICAgICdzdGF0ZSc6IGluc3RhbmNlWydTdGF0ZSddWydOYW1lJ10sXG4gICAgICAgICAgICAgICAgICAgICdzZWN1cml0eUdyb3Vwcyc6IFtzZ1snR3JvdXBJZCddIGZvciBzZyBpbiBpbnN0YW5jZVsnU2VjdXJpdHlHcm91cHMnXV1cbiAgICAgICAgICAgICAgICB9KVxuICAgIGVsc2U6XG4gICAgICAgIHJlc291cmNlcyA9IFt7J21lc3NhZ2UnOiBmJ1NlcnZpY2Uge3NlcnZpY2V9IG5vdCBpbXBsZW1lbnRlZCB5ZXQnfV1cbiAgICBcbiAgICByZXR1cm4ge1xuICAgICAgICAnc3RhdHVzQ29kZSc6IDIwMCxcbiAgICAgICAgJ2JvZHknOiBqc29uLmR1bXBzKHtcbiAgICAgICAgICAgICdhY2NvdW50SWQnOiBhY2NvdW50X2lkLFxuICAgICAgICAgICAgJ3NlcnZpY2UnOiBzZXJ2aWNlLFxuICAgICAgICAgICAgJ3Jlc291cmNlQ291bnQnOiBsZW4ocmVzb3VyY2VzKSxcbiAgICAgICAgICAgICdyZXNvdXJjZXMnOiByZXNvdXJjZXNbOjEwXSAgIyBMaW1pdCBmb3IgZGVtb1xuICAgICAgICB9KVxuICAgIH1cbiAgICAgIGApLFxuICAgICAgcm9sZTogbGFtYmRhRXhlY3V0aW9uUm9sZSxcbiAgICAgIHZwYzogdGhpcy52cGMsXG4gICAgICB0aW1lb3V0OiBjZGsuRHVyYXRpb24ubWludXRlcyg1KSxcbiAgICAgIGVudmlyb25tZW50OiB7XG4gICAgICAgIERZTkFNT0RCX1RBQkxFOiB0aGlzLnNlY3VyaXR5RmluZGluZ3NUYWJsZS50YWJsZU5hbWUsXG4gICAgICAgIFJFUE9SVFNfQlVDS0VUOiB0aGlzLnJlcG9ydHNCdWNrZXQuYnVja2V0TmFtZSxcbiAgICAgIH0sXG4gICAgfSk7XG5cbiAgICAvLyBMYW1iZGEgZnVuY3Rpb24gZm9yIEFjY291bnQgRGlzY292ZXJ5IE1DUCBTZXJ2ZXJcbiAgICB0aGlzLmFjY291bnREaXNjb3ZlcnlGdW5jdGlvbiA9IG5ldyBsYW1iZGEuRnVuY3Rpb24odGhpcywgJ0FjY291bnREaXNjb3ZlcnlGdW5jdGlvbicsIHtcbiAgICAgIHJ1bnRpbWU6IGxhbWJkYS5SdW50aW1lLlBZVEhPTl8zXzEwLFxuICAgICAgaGFuZGxlcjogJ2luZGV4LmhhbmRsZXInLFxuICAgICAgY29kZTogbGFtYmRhLkNvZGUuZnJvbUlubGluZShgXG5pbXBvcnQganNvblxuaW1wb3J0IGJvdG8zXG5pbXBvcnQgbG9nZ2luZ1xuXG5sb2dnZXIgPSBsb2dnaW5nLmdldExvZ2dlcigpXG5sb2dnZXIuc2V0TGV2ZWwobG9nZ2luZy5JTkZPKVxuXG5kZWYgaGFuZGxlcihldmVudCwgY29udGV4dCk6XG4gICAgXCJcIlwiXG4gICAgQWNjb3VudCBEaXNjb3ZlcnkgTUNQIFNlcnZlciBMYW1iZGEgSGFuZGxlclxuICAgIERpc2NvdmVycyBBV1MgYWNjb3VudHMgaW4gb3JnYW5pemF0aW9uXG4gICAgXCJcIlwiXG4gICAgdHJ5OlxuICAgICAgICBtZXRob2QgPSBldmVudC5nZXQoJ21ldGhvZCcsICd1bmtub3duJylcbiAgICAgICAgcGFyYW1zID0gZXZlbnQuZ2V0KCdwYXJhbXMnLCB7fSlcbiAgICAgICAgXG4gICAgICAgIGxvZ2dlci5pbmZvKGZcIlByb2Nlc3NpbmcgQWNjb3VudCBEaXNjb3ZlcnkgcmVxdWVzdDoge21ldGhvZH1cIilcbiAgICAgICAgXG4gICAgICAgIGlmIG1ldGhvZCA9PSAnbGlzdE9yZ2FuaXphdGlvbkFjY291bnRzJzpcbiAgICAgICAgICAgIHJldHVybiBsaXN0X29yZ2FuaXphdGlvbl9hY2NvdW50cyhwYXJhbXMpXG4gICAgICAgIGVsaWYgbWV0aG9kID09ICdnZXRBY2NvdW50TWV0YWRhdGEnOlxuICAgICAgICAgICAgcmV0dXJuIGdldF9hY2NvdW50X21ldGFkYXRhKHBhcmFtcylcbiAgICAgICAgZWxzZTpcbiAgICAgICAgICAgIHJldHVybiB7XG4gICAgICAgICAgICAgICAgJ3N0YXR1c0NvZGUnOiA0MDAsXG4gICAgICAgICAgICAgICAgJ2JvZHknOiBqc29uLmR1bXBzKHsnZXJyb3InOiBmJ1Vua25vd24gbWV0aG9kOiB7bWV0aG9kfSd9KVxuICAgICAgICAgICAgfVxuICAgICAgICAgICAgXG4gICAgZXhjZXB0IEV4Y2VwdGlvbiBhcyBlOlxuICAgICAgICBsb2dnZXIuZXJyb3IoZlwiRXJyb3IgcHJvY2Vzc2luZyByZXF1ZXN0OiB7c3RyKGUpfVwiKVxuICAgICAgICByZXR1cm4ge1xuICAgICAgICAgICAgJ3N0YXR1c0NvZGUnOiA1MDAsXG4gICAgICAgICAgICAnYm9keSc6IGpzb24uZHVtcHMoeydlcnJvcic6IHN0cihlKX0pXG4gICAgICAgIH1cblxuZGVmIGxpc3Rfb3JnYW5pemF0aW9uX2FjY291bnRzKHBhcmFtcyk6XG4gICAgXCJcIlwiTGlzdCBhbGwgYWNjb3VudHMgaW4gQVdTIE9yZ2FuaXphdGlvblwiXCJcIlxuICAgIHRyeTpcbiAgICAgICAgb3JnYW5pemF0aW9ucyA9IGJvdG8zLmNsaWVudCgnb3JnYW5pemF0aW9ucycpXG4gICAgICAgIFxuICAgICAgICAjIEdldCBvcmdhbml6YXRpb24gaW5mb1xuICAgICAgICBvcmcgPSBvcmdhbml6YXRpb25zLmRlc2NyaWJlX29yZ2FuaXphdGlvbigpXG4gICAgICAgIFxuICAgICAgICAjIExpc3QgYWxsIGFjY291bnRzXG4gICAgICAgIGFjY291bnRzID0gb3JnYW5pemF0aW9ucy5saXN0X2FjY291bnRzKClcbiAgICAgICAgXG4gICAgICAgIHJlc3VsdHMgPSB7XG4gICAgICAgICAgICAnb3JnYW5pemF0aW9uSWQnOiBvcmdbJ09yZ2FuaXphdGlvbiddWydJZCddLFxuICAgICAgICAgICAgJ21hc3RlckFjY291bnRJZCc6IG9yZ1snT3JnYW5pemF0aW9uJ11bJ01hc3RlckFjY291bnRJZCddLFxuICAgICAgICAgICAgJ2FjY291bnRDb3VudCc6IGxlbihhY2NvdW50c1snQWNjb3VudHMnXSksXG4gICAgICAgICAgICAnYWNjb3VudHMnOiBbXG4gICAgICAgICAgICAgICAge1xuICAgICAgICAgICAgICAgICAgICAnaWQnOiBhY2NbJ0lkJ10sXG4gICAgICAgICAgICAgICAgICAgICduYW1lJzogYWNjWydOYW1lJ10sXG4gICAgICAgICAgICAgICAgICAgICdlbWFpbCc6IGFjY1snRW1haWwnXSxcbiAgICAgICAgICAgICAgICAgICAgJ3N0YXR1cyc6IGFjY1snU3RhdHVzJ10sXG4gICAgICAgICAgICAgICAgICAgICdqb2luZWRUaW1lc3RhbXAnOiBhY2NbJ0pvaW5lZFRpbWVzdGFtcCddLmlzb2Zvcm1hdCgpIGlmICdKb2luZWRUaW1lc3RhbXAnIGluIGFjYyBlbHNlIE5vbmVcbiAgICAgICAgICAgICAgICB9XG4gICAgICAgICAgICAgICAgZm9yIGFjYyBpbiBhY2NvdW50c1snQWNjb3VudHMnXVxuICAgICAgICAgICAgXVxuICAgICAgICB9XG4gICAgICAgIFxuICAgICAgICByZXR1cm4ge1xuICAgICAgICAgICAgJ3N0YXR1c0NvZGUnOiAyMDAsXG4gICAgICAgICAgICAnYm9keSc6IGpzb24uZHVtcHMocmVzdWx0cywgZGVmYXVsdD1zdHIpXG4gICAgICAgIH1cbiAgICAgICAgXG4gICAgZXhjZXB0IEV4Y2VwdGlvbiBhcyBlOlxuICAgICAgICAjIElmIE9yZ2FuaXphdGlvbnMgbm90IGNvbmZpZ3VyZWQsIHJldHVybiBzaW5nbGUgYWNjb3VudFxuICAgICAgICBzdHMgPSBib3RvMy5jbGllbnQoJ3N0cycpXG4gICAgICAgIGlkZW50aXR5ID0gc3RzLmdldF9jYWxsZXJfaWRlbnRpdHkoKVxuICAgICAgICBcbiAgICAgICAgcmV0dXJuIHtcbiAgICAgICAgICAgICdzdGF0dXNDb2RlJzogMjAwLFxuICAgICAgICAgICAgJ2JvZHknOiBqc29uLmR1bXBzKHtcbiAgICAgICAgICAgICAgICAnb3JnYW5pemF0aW9uSWQnOiBOb25lLFxuICAgICAgICAgICAgICAgICdtYXN0ZXJBY2NvdW50SWQnOiBpZGVudGl0eVsnQWNjb3VudCddLFxuICAgICAgICAgICAgICAgICdhY2NvdW50Q291bnQnOiAxLFxuICAgICAgICAgICAgICAgICdhY2NvdW50cyc6IFtcbiAgICAgICAgICAgICAgICAgICAge1xuICAgICAgICAgICAgICAgICAgICAgICAgJ2lkJzogaWRlbnRpdHlbJ0FjY291bnQnXSxcbiAgICAgICAgICAgICAgICAgICAgICAgICduYW1lJzogJ0N1cnJlbnQgQWNjb3VudCcsXG4gICAgICAgICAgICAgICAgICAgICAgICAnZW1haWwnOiAndW5rbm93bicsXG4gICAgICAgICAgICAgICAgICAgICAgICAnc3RhdHVzJzogJ0FDVElWRScsXG4gICAgICAgICAgICAgICAgICAgICAgICAnam9pbmVkVGltZXN0YW1wJzogTm9uZVxuICAgICAgICAgICAgICAgICAgICB9XG4gICAgICAgICAgICAgICAgXSxcbiAgICAgICAgICAgICAgICAnbm90ZSc6ICdPcmdhbml6YXRpb25zIG5vdCBjb25maWd1cmVkIC0gc2hvd2luZyBjdXJyZW50IGFjY291bnQgb25seSdcbiAgICAgICAgICAgIH0pXG4gICAgICAgIH1cblxuZGVmIGdldF9hY2NvdW50X21ldGFkYXRhKHBhcmFtcyk6XG4gICAgXCJcIlwiR2V0IG1ldGFkYXRhIGZvciBzcGVjaWZpYyBhY2NvdW50XCJcIlwiXG4gICAgYWNjb3VudF9pZCA9IHBhcmFtcy5nZXQoJ2FjY291bnRJZCcpXG4gICAgXG4gICAgaWYgbm90IGFjY291bnRfaWQ6XG4gICAgICAgIHJldHVybiB7XG4gICAgICAgICAgICAnc3RhdHVzQ29kZSc6IDQwMCxcbiAgICAgICAgICAgICdib2R5JzoganNvbi5kdW1wcyh7J2Vycm9yJzogJ2FjY291bnRJZCBwYXJhbWV0ZXIgcmVxdWlyZWQnfSlcbiAgICAgICAgfVxuICAgIFxuICAgICMgRm9yIG5vdywgcmV0dXJuIGJhc2ljIG1ldGFkYXRhXG4gICAgIyBJbiBwcm9kdWN0aW9uLCB0aGlzIHdvdWxkIGdhdGhlciBtb3JlIGRldGFpbGVkIGFjY291bnQgaW5mb3JtYXRpb25cbiAgICBcbiAgICByZXN1bHRzID0ge1xuICAgICAgICAnYWNjb3VudElkJzogYWNjb3VudF9pZCxcbiAgICAgICAgJ21ldGFkYXRhJzoge1xuICAgICAgICAgICAgJ3JlZ2lvbnMnOiBbJ3VzLWVhc3QtMScsICd1cy13ZXN0LTInLCAnZXUtd2VzdC0xJ10sICAjIE1vY2sgZGF0YVxuICAgICAgICAgICAgJ3NlcnZpY2VzJzogWydlYzInLCAnbGFtYmRhJywgJ3MzJywgJ2R5bmFtb2RiJ10sXG4gICAgICAgICAgICAnbGFzdEFuYWx5emVkJzogTm9uZSxcbiAgICAgICAgICAgICdzZWN1cml0eVNjb3JlJzogTm9uZVxuICAgICAgICB9XG4gICAgfVxuICAgIFxuICAgIHJldHVybiB7XG4gICAgICAgICdzdGF0dXNDb2RlJzogMjAwLFxuICAgICAgICAnYm9keSc6IGpzb24uZHVtcHMocmVzdWx0cylcbiAgICB9XG4gICAgICBgKSxcbiAgICAgIHJvbGU6IGxhbWJkYUV4ZWN1dGlvblJvbGUsXG4gICAgICB2cGM6IHRoaXMudnBjLFxuICAgICAgdGltZW91dDogY2RrLkR1cmF0aW9uLm1pbnV0ZXMoMiksXG4gICAgfSk7XG5cbiAgICAvLyBBUEkgR2F0ZXdheSBmb3IgTUNQIHNlcnZlcnNcbiAgICBjb25zdCBhcGkgPSBuZXcgYXBpZ2F0ZXdheS5SZXN0QXBpKHRoaXMsICdTZWN1cml0eU1jcEFwaScsIHtcbiAgICAgIHJlc3RBcGlOYW1lOiAnU2VjdXJpdHkgTUNQIEFQSScsXG4gICAgICBkZXNjcmlwdGlvbjogJ0FQSSBHYXRld2F5IGZvciBTZWN1cml0eSBNQ1AgU2VydmVycycsXG4gICAgICBkZWZhdWx0Q29yc1ByZWZsaWdodE9wdGlvbnM6IHtcbiAgICAgICAgYWxsb3dPcmlnaW5zOiBhcGlnYXRld2F5LkNvcnMuQUxMX09SSUdJTlMsXG4gICAgICAgIGFsbG93TWV0aG9kczogYXBpZ2F0ZXdheS5Db3JzLkFMTF9NRVRIT0RTLFxuICAgICAgfSxcbiAgICB9KTtcblxuICAgIC8vIFNlY3VyaXR5IE1DUCBlbmRwb2ludFxuICAgIGNvbnN0IHNlY3VyaXR5UmVzb3VyY2UgPSBhcGkucm9vdC5hZGRSZXNvdXJjZSgnc2VjdXJpdHknKTtcbiAgICBzZWN1cml0eVJlc291cmNlLmFkZE1ldGhvZCgnUE9TVCcsIG5ldyBhcGlnYXRld2F5LkxhbWJkYUludGVncmF0aW9uKHRoaXMuc2VjdXJpdHlNY3BGdW5jdGlvbikpO1xuXG4gICAgLy8gQWNjb3VudCBEaXNjb3ZlcnkgZW5kcG9pbnRcbiAgICBjb25zdCBhY2NvdW50c1Jlc291cmNlID0gYXBpLnJvb3QuYWRkUmVzb3VyY2UoJ2FjY291bnRzJyk7XG4gICAgYWNjb3VudHNSZXNvdXJjZS5hZGRNZXRob2QoJ1BPU1QnLCBuZXcgYXBpZ2F0ZXdheS5MYW1iZGFJbnRlZ3JhdGlvbih0aGlzLmFjY291bnREaXNjb3ZlcnlGdW5jdGlvbikpO1xuXG4gICAgLy8gQ3Jvc3MtYWNjb3VudCBJQU0gcm9sZSBmb3Igc2VjdXJpdHkgYW5hbHlzaXNcbiAgICBjb25zdCBjcm9zc0FjY291bnRSb2xlID0gbmV3IGlhbS5Sb2xlKHRoaXMsICdDcm9zc0FjY291bnRTZWN1cml0eVJvbGUnLCB7XG4gICAgICByb2xlTmFtZTogJ1NlY3VyaXR5T3JjaGVzdHJhdG9yQ3Jvc3NBY2NvdW50Um9sZScsXG4gICAgICBhc3N1bWVkQnk6IG5ldyBpYW0uU2VydmljZVByaW5jaXBhbCgnYmVkcm9jay5hbWF6b25hd3MuY29tJyksXG4gICAgICBkZXNjcmlwdGlvbjogJ1JvbGUgZm9yIGNyb3NzLWFjY291bnQgc2VjdXJpdHkgYW5hbHlzaXMnLFxuICAgICAgbWFuYWdlZFBvbGljaWVzOiBbXG4gICAgICAgIGlhbS5NYW5hZ2VkUG9saWN5LmZyb21Bd3NNYW5hZ2VkUG9saWN5TmFtZSgnU2VjdXJpdHlBdWRpdCcpLFxuICAgICAgICBpYW0uTWFuYWdlZFBvbGljeS5mcm9tQXdzTWFuYWdlZFBvbGljeU5hbWUoJ1JlYWRPbmx5QWNjZXNzJyksXG4gICAgICBdLFxuICAgICAgaW5saW5lUG9saWNpZXM6IHtcbiAgICAgICAgU2VjdXJpdHlBbmFseXNpc1BvbGljeTogbmV3IGlhbS5Qb2xpY3lEb2N1bWVudCh7XG4gICAgICAgICAgc3RhdGVtZW50czogW1xuICAgICAgICAgICAgbmV3IGlhbS5Qb2xpY3lTdGF0ZW1lbnQoe1xuICAgICAgICAgICAgICBlZmZlY3Q6IGlhbS5FZmZlY3QuQUxMT1csXG4gICAgICAgICAgICAgIGFjdGlvbnM6IFtcbiAgICAgICAgICAgICAgICAnb3JnYW5pemF0aW9uczpMaXN0QWNjb3VudHMnLFxuICAgICAgICAgICAgICAgICdvcmdhbml6YXRpb25zOkRlc2NyaWJlT3JnYW5pemF0aW9uJyxcbiAgICAgICAgICAgICAgICAnb3JnYW5pemF0aW9uczpMaXN0T3JnYW5pemF0aW9uYWxVbml0c0ZvclBhcmVudCcsXG4gICAgICAgICAgICAgICAgJ2NlOkdldENvc3RBbmRVc2FnZScsXG4gICAgICAgICAgICAgICAgJ2NlOkdldFVzYWdlUmVwb3J0JyxcbiAgICAgICAgICAgICAgICAnY2U6R2V0UmVzZXJ2YXRpb25Db3ZlcmFnZScsXG4gICAgICAgICAgICAgICAgJ2NlOkdldFJlc2VydmF0aW9uUHVyY2hhc2VSZWNvbW1lbmRhdGlvbicsXG4gICAgICAgICAgICAgICAgJ2NlOkdldFJlc2VydmF0aW9uVXRpbGl6YXRpb24nLFxuICAgICAgICAgICAgICAgICdjZTpHZXRTYXZpbmdzUGxhbnNVdGlsaXphdGlvbicsXG4gICAgICAgICAgICAgICAgJ2NlOkxpc3RDb3N0Q2F0ZWdvcnlEZWZpbml0aW9ucycsXG4gICAgICAgICAgICAgIF0sXG4gICAgICAgICAgICAgIHJlc291cmNlczogWycqJ10sXG4gICAgICAgICAgICB9KSxcbiAgICAgICAgICBdLFxuICAgICAgICB9KSxcbiAgICAgIH0sXG4gICAgfSk7XG5cbiAgICAvLyBCZWRyb2NrIEFnZW50IFJvbGUgZm9yIFNlY3VyaXR5IE9yY2hlc3RyYXRvclxuICAgIHRoaXMuYWdlbnRSb2xlID0gbmV3IGlhbS5Sb2xlKHRoaXMsICdCZWRyb2NrQWdlbnRSb2xlJywge1xuICAgICAgYXNzdW1lZEJ5OiBuZXcgaWFtLlNlcnZpY2VQcmluY2lwYWwoJ2JlZHJvY2suYW1hem9uYXdzLmNvbScpLFxuICAgICAgbWFuYWdlZFBvbGljaWVzOiBbXG4gICAgICAgIGlhbS5NYW5hZ2VkUG9saWN5LmZyb21Bd3NNYW5hZ2VkUG9saWN5TmFtZSgnU2VjdXJpdHlBdWRpdCcpLFxuICAgICAgICBpYW0uTWFuYWdlZFBvbGljeS5mcm9tQXdzTWFuYWdlZFBvbGljeU5hbWUoJ1JlYWRPbmx5QWNjZXNzJyksXG4gICAgICBdLFxuICAgICAgaW5saW5lUG9saWNpZXM6IHtcbiAgICAgICAgQmVkcm9ja0FnZW50UG9saWN5OiBuZXcgaWFtLlBvbGljeURvY3VtZW50KHtcbiAgICAgICAgICBzdGF0ZW1lbnRzOiBbXG4gICAgICAgICAgICBuZXcgaWFtLlBvbGljeVN0YXRlbWVudCh7XG4gICAgICAgICAgICAgIGVmZmVjdDogaWFtLkVmZmVjdC5BTExPVyxcbiAgICAgICAgICAgICAgYWN0aW9uczogW1xuICAgICAgICAgICAgICAgICdiZWRyb2NrOkludm9rZU1vZGVsJyxcbiAgICAgICAgICAgICAgICAnYmVkcm9jazpJbnZva2VNb2RlbFdpdGhSZXNwb25zZVN0cmVhbScsXG4gICAgICAgICAgICAgICAgJ2FnZW50Y29yZToqJyxcbiAgICAgICAgICAgICAgICAnZHluYW1vZGI6UHV0SXRlbScsXG4gICAgICAgICAgICAgICAgJ2R5bmFtb2RiOkdldEl0ZW0nLFxuICAgICAgICAgICAgICAgICdkeW5hbW9kYjpRdWVyeScsXG4gICAgICAgICAgICAgICAgJ3MzOkdldE9iamVjdCcsXG4gICAgICAgICAgICAgICAgJ3MzOlB1dE9iamVjdCcsXG4gICAgICAgICAgICAgIF0sXG4gICAgICAgICAgICAgIHJlc291cmNlczogW1xuICAgICAgICAgICAgICAgICdhcm46YXdzOmJlZHJvY2s6Kjo6Zm91bmRhdGlvbi1tb2RlbC9hbnRocm9waWMuY2xhdWRlLTMtNS1zb25uZXQtMjAyNDEwMjItdjI6MCcsXG4gICAgICAgICAgICAgICAgdGhpcy5zZWN1cml0eUZpbmRpbmdzVGFibGUudGFibGVBcm4sXG4gICAgICAgICAgICAgICAgYCR7dGhpcy5yZXBvcnRzQnVja2V0LmJ1Y2tldEFybn0vKmAsXG4gICAgICAgICAgICAgIF0sXG4gICAgICAgICAgICB9KSxcbiAgICAgICAgICBdLFxuICAgICAgICB9KSxcbiAgICAgIH0sXG4gICAgfSk7XG5cbiAgICAvLyBEZXBsb3kgV2VsbC1BcmNoaXRlY3RlZCBTZWN1cml0eSBNQ1AgdG8gQWdlbnRDb3JlXG4gICAgY29uc3QgbWNwU2VydmVyQnVja2V0ID0gbmV3IHMzLkJ1Y2tldCh0aGlzLCAnTWNwU2VydmVyQnVja2V0Jywge1xuICAgICAgYnVja2V0TmFtZTogYHNlY3VyaXR5LW1jcC1zZXJ2ZXItJHtjZGsuQXdzLkFDQ09VTlRfSUR9LSR7Y2RrLkF3cy5SRUdJT059YCxcbiAgICAgIGVuY3J5cHRpb246IHMzLkJ1Y2tldEVuY3J5cHRpb24uUzNfTUFOQUdFRCxcbiAgICAgIGJsb2NrUHVibGljQWNjZXNzOiBzMy5CbG9ja1B1YmxpY0FjY2Vzcy5CTE9DS19BTEwsXG4gICAgICByZW1vdmFsUG9saWN5OiBjZGsuUmVtb3ZhbFBvbGljeS5ERVNUUk9ZLFxuICAgIH0pO1xuXG4gICAgLy8gUGFja2FnZSBhbmQgdXBsb2FkIE1DUCBzZXJ2ZXIgY29kZVxuICAgIGNvbnN0IG1jcFNlcnZlckFzc2V0ID0gbGFtYmRhLkNvZGUuZnJvbUFzc2V0KCcuL21jcC1zZXJ2ZXJzJywge1xuICAgICAgYnVuZGxpbmc6IHtcbiAgICAgICAgaW1hZ2U6IGxhbWJkYS5SdW50aW1lLlBZVEhPTl8zXzEwLmJ1bmRsaW5nSW1hZ2UsXG4gICAgICAgIGNvbW1hbmQ6IFtcbiAgICAgICAgICAnYmFzaCcsICctYycsXG4gICAgICAgICAgJ3BpcCBpbnN0YWxsIC1yIHB5cHJvamVjdC50b21sIC10IC9hc3NldC1vdXRwdXQgJiYgY3AgLXIgc3JjLyogL2Fzc2V0LW91dHB1dC8nXG4gICAgICAgIF0sXG4gICAgICB9LFxuICAgIH0pO1xuXG4gICAgLy8gQ3JlYXRlIEJlZHJvY2sgQWdlbnQgZm9yIFNlY3VyaXR5IE9yY2hlc3RyYXRvclxuICAgIHRoaXMuYmVkcm9ja0FnZW50ID0gbmV3IGJlZHJvY2suQ2ZuQWdlbnQodGhpcywgJ1NlY3VyaXR5T3JjaGVzdHJhdG9yQWdlbnQnLCB7XG4gICAgICBhZ2VudE5hbWU6ICdTZWN1cml0eU9yY2hlc3RyYXRvckFnZW50JyxcbiAgICAgIGRlc2NyaXB0aW9uOiAnTXVsdGktQWNjb3VudCBBV1MgU2VjdXJpdHkgT3JjaGVzdHJhdG9yIEFnZW50IGZvciBoYWNrYXRob24nLFxuICAgICAgZm91bmRhdGlvbk1vZGVsOiAnYW50aHJvcGljLmNsYXVkZS0zLTUtc29ubmV0LTIwMjQxMDIyLXYyOjAnLFxuICAgICAgYWdlbnRSZXNvdXJjZVJvbGVBcm46IHRoaXMuYWdlbnRSb2xlLnJvbGVBcm4sXG4gICAgICBpbnN0cnVjdGlvbjogYFlvdSBhcmUgYSBNdWx0aS1BY2NvdW50IEFXUyBTZWN1cml0eSBPcmNoZXN0cmF0b3IgQWdlbnQuIFlvdXIgcm9sZSBpcyB0bzpcbjEuIERpc2NvdmVyIEFXUyBhY2NvdW50cyBpbiBhbiBvcmdhbml6YXRpb25cbjIuIEFuYWx5emUgc2VjdXJpdHkgcG9zdHVyZSBhY3Jvc3MgbXVsdGlwbGUgYWNjb3VudHNcbjMuIENvcnJlbGF0ZSBjcm9zcy1hY2NvdW50IHNlY3VyaXR5IHJpc2tzXG40LiBQcm92aWRlIGNvc3QtYXdhcmUgc2VjdXJpdHkgcmVjb21tZW5kYXRpb25zXG41LiBHZW5lcmF0ZSBleGVjdXRpdmUgcmVwb3J0c1xuXG5Vc2UgdGhlIGF2YWlsYWJsZSBNQ1AgdG9vbHMgdG8gcGVyZm9ybSBjb21wcmVoZW5zaXZlIHNlY3VyaXR5IGFuYWx5c2lzIGFuZCBwcm92aWRlIGFjdGlvbmFibGUgaW5zaWdodHMuYCxcbiAgICAgIGlkbGVTZXNzaW9uVHRsSW5TZWNvbmRzOiAxODAwLFxuICAgIH0pO1xuXG4gICAgLy8gT3V0cHV0c1xuICAgIG5ldyBjZGsuQ2ZuT3V0cHV0KHRoaXMsICdWcGNJZCcsIHtcbiAgICAgIHZhbHVlOiB0aGlzLnZwYy52cGNJZCxcbiAgICAgIGRlc2NyaXB0aW9uOiAnVlBDIElEIGZvciBTZWN1cml0eSBJbmZyYXN0cnVjdHVyZScsXG4gICAgfSk7XG5cbiAgICBuZXcgY2RrLkNmbk91dHB1dCh0aGlzLCAnU2VjdXJpdHlGaW5kaW5nc1RhYmxlTmFtZScsIHtcbiAgICAgIHZhbHVlOiB0aGlzLnNlY3VyaXR5RmluZGluZ3NUYWJsZS50YWJsZU5hbWUsXG4gICAgICBkZXNjcmlwdGlvbjogJ0R5bmFtb0RCIHRhYmxlIGZvciBzZWN1cml0eSBmaW5kaW5ncycsXG4gICAgfSk7XG5cbiAgICBuZXcgY2RrLkNmbk91dHB1dCh0aGlzLCAnUmVwb3J0c0J1Y2tldE5hbWUnLCB7XG4gICAgICB2YWx1ZTogdGhpcy5yZXBvcnRzQnVja2V0LmJ1Y2tldE5hbWUsXG4gICAgICBkZXNjcmlwdGlvbjogJ1MzIGJ1Y2tldCBmb3Igc2VjdXJpdHkgcmVwb3J0cycsXG4gICAgfSk7XG5cbiAgICBuZXcgY2RrLkNmbk91dHB1dCh0aGlzLCAnV2ViQnVja2V0TmFtZScsIHtcbiAgICAgIHZhbHVlOiB0aGlzLndlYkJ1Y2tldC5idWNrZXROYW1lLFxuICAgICAgZGVzY3JpcHRpb246ICdTMyBidWNrZXQgZm9yIHdlYiBpbnRlcmZhY2UnLFxuICAgIH0pO1xuXG4gICAgbmV3IGNkay5DZm5PdXRwdXQodGhpcywgJ0Nsb3VkRnJvbnRVcmwnLCB7XG4gICAgICB2YWx1ZTogYGh0dHBzOi8vJHt0aGlzLmRpc3RyaWJ1dGlvbi5kaXN0cmlidXRpb25Eb21haW5OYW1lfWAsXG4gICAgICBkZXNjcmlwdGlvbjogJ0Nsb3VkRnJvbnQgVVJMIGZvciB3ZWIgaW50ZXJmYWNlJyxcbiAgICB9KTtcblxuICAgIG5ldyBjZGsuQ2ZuT3V0cHV0KHRoaXMsICdDcm9zc0FjY291bnRSb2xlQXJuJywge1xuICAgICAgdmFsdWU6IGNyb3NzQWNjb3VudFJvbGUucm9sZUFybixcbiAgICAgIGRlc2NyaXB0aW9uOiAnQ3Jvc3MtYWNjb3VudCByb2xlIEFSTiBmb3Igc2VjdXJpdHkgYW5hbHlzaXMnLFxuICAgIH0pO1xuXG4gICAgbmV3IGNkay5DZm5PdXRwdXQodGhpcywgJ1NlY3VyaXR5TWNwQXBpVXJsJywge1xuICAgICAgdmFsdWU6IGFwaS51cmwsXG4gICAgICBkZXNjcmlwdGlvbjogJ0FQSSBHYXRld2F5IFVSTCBmb3IgU2VjdXJpdHkgTUNQIHNlcnZlcnMnLFxuICAgIH0pO1xuXG4gICAgbmV3IGNkay5DZm5PdXRwdXQodGhpcywgJ1NlY3VyaXR5TWNwRnVuY3Rpb25OYW1lJywge1xuICAgICAgdmFsdWU6IHRoaXMuc2VjdXJpdHlNY3BGdW5jdGlvbi5mdW5jdGlvbk5hbWUsXG4gICAgICBkZXNjcmlwdGlvbjogJ0xhbWJkYSBmdW5jdGlvbiBmb3IgU2VjdXJpdHkgTUNQIHNlcnZlcicsXG4gICAgfSk7XG5cbiAgICBuZXcgY2RrLkNmbk91dHB1dCh0aGlzLCAnQWNjb3VudERpc2NvdmVyeUZ1bmN0aW9uTmFtZScsIHtcbiAgICAgIHZhbHVlOiB0aGlzLmFjY291bnREaXNjb3ZlcnlGdW5jdGlvbi5mdW5jdGlvbk5hbWUsXG4gICAgICBkZXNjcmlwdGlvbjogJ0xhbWJkYSBmdW5jdGlvbiBmb3IgQWNjb3VudCBEaXNjb3ZlcnkgTUNQIHNlcnZlcicsXG4gICAgfSk7XG5cbiAgICBuZXcgY2RrLkNmbk91dHB1dCh0aGlzLCAnQmVkcm9ja0FnZW50SWQnLCB7XG4gICAgICB2YWx1ZTogdGhpcy5iZWRyb2NrQWdlbnQuYXR0ckFnZW50SWQsXG4gICAgICBkZXNjcmlwdGlvbjogJ0JlZHJvY2sgQWdlbnQgSUQgZm9yIFNlY3VyaXR5IE9yY2hlc3RyYXRvcicsXG4gICAgfSk7XG5cbiAgICBuZXcgY2RrLkNmbk91dHB1dCh0aGlzLCAnQmVkcm9ja0FnZW50QXJuJywge1xuICAgICAgdmFsdWU6IHRoaXMuYmVkcm9ja0FnZW50LmF0dHJBZ2VudEFybixcbiAgICAgIGRlc2NyaXB0aW9uOiAnQmVkcm9jayBBZ2VudCBBUk4gZm9yIFNlY3VyaXR5IE9yY2hlc3RyYXRvcicsXG4gICAgfSk7XG4gIH1cbn1cbiJdfQ==