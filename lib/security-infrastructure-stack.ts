import * as cdk from 'aws-cdk-lib';
import * as ec2 from 'aws-cdk-lib/aws-ec2';
import * as iam from 'aws-cdk-lib/aws-iam';
import * as dynamodb from 'aws-cdk-lib/aws-dynamodb';
import * as s3 from 'aws-cdk-lib/aws-s3';
import * as cloudfront from 'aws-cdk-lib/aws-cloudfront';
import * as origins from 'aws-cdk-lib/aws-cloudfront-origins';
import { Construct } from 'constructs';

export class SecurityInfrastructureStack extends cdk.Stack {
  public readonly vpc: ec2.Vpc;
  public readonly securityFindingsTable: dynamodb.Table;
  public readonly reportsBucket: s3.Bucket;
  public readonly webBucket: s3.Bucket;
  public readonly distribution: cloudfront.Distribution;

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
  }
}
