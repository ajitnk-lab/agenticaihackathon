#!/usr/bin/env node
import 'source-map-support/register';
import * as cdk from 'aws-cdk-lib';
import { SecurityInfrastructureStack } from '../lib/security-infrastructure-stack';

const app = new cdk.App();

new SecurityInfrastructureStack(app, 'SecurityInfrastructureStack', {
  env: {
    account: process.env.CDK_DEFAULT_ACCOUNT,
    region: process.env.CDK_DEFAULT_REGION || 'us-east-1',
  },
});
