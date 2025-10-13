#!/usr/bin/env node
import 'source-map-support/register';
import * as cdk from 'aws-cdk-lib';
import { SecurityOrchestratorStack } from '../lib/security-orchestrator-stack';

const app = new cdk.App();

new SecurityOrchestratorStack(app, 'SecurityOrchestratorStack', {
  env: {
    account: process.env.CDK_DEFAULT_ACCOUNT,
    region: process.env.CDK_DEFAULT_REGION || 'us-east-1',
  },
});
