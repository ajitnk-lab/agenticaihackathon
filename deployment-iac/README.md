# 🚀 AgentCore Security Dashboard - Infrastructure as Code

## 📦 **One-Click Deployment**

Deploy the complete AgentCore Security Dashboard to any AWS account with a single command.

### **Quick Start**

```bash
# Clone repository
git clone https://github.com/ajitnk-lab/agenticaihackathon.git
cd agenticaihackathon/deployment-iac

# Deploy to AWS
./scripts/deploy.sh
```

### **Prerequisites**

- AWS CLI installed and configured
- AWS account with appropriate permissions
- Bash shell (Linux/macOS/WSL)

## 🏗️ **Infrastructure Components**

### **AWS Resources Created**
- **2 Lambda Functions** → Main dashboard + Recommendations
- **2 Function URLs** → Public HTTPS endpoints
- **1 IAM Role** → Lambda execution permissions
- **CloudFormation Stack** → Infrastructure management

### **Deployment Options**

#### **Option 1: CloudFormation (Recommended)**
```bash
cd deployment-iac
./scripts/deploy.sh
```

#### **Option 2: Terraform**
```bash
cd deployment-iac/terraform
terraform init
terraform plan
terraform apply
```

#### **Option 3: Manual CloudFormation**
```bash
aws cloudformation deploy \
  --template-file cloudformation/template.yaml \
  --stack-name agentcore-security-dashboard-stack \
  --capabilities CAPABILITY_NAMED_IAM
```

## 📊 **What Gets Deployed**

### **Main Dashboard**
- **Interactive security metrics** (Security Score: 85, Findings: 151)
- **Cost analysis** ($128/month, 23,337% ROI)
- **Real-time charts** with Chart.js integration
- **Responsive design** for all devices

### **Recommendations Page**
- **Priority-based security recommendations**
- **Cost optimization opportunities**
- **Interactive action buttons**
- **Color-coded severity levels**

## 🔧 **Configuration**

### **Environment Variables**
```bash
export AWS_REGION=us-east-1          # AWS region (default: us-east-1)
export PROJECT_NAME=my-dashboard     # Project name (default: agentcore-security-dashboard)
```

### **Customization**
- Edit `cloudformation/template.yaml` for infrastructure changes
- Modify `scripts/deploy.sh` for deployment customization
- Update Lambda code in deployment assets

## 📈 **Deployment Outputs**

After successful deployment:
```
🎉 Deployment Complete!
==================================
📊 Main Dashboard: https://xyz.lambda-url.us-east-1.on.aws/
🎯 Recommendations: https://abc.lambda-url.us-east-1.on.aws/
==================================
```

## 🗑️ **Cleanup**

Remove all AWS resources:
```bash
./scripts/destroy.sh
```

## 📋 **File Structure**

```
deployment-iac/
├── terraform/
│   └── main.tf                 # Terraform infrastructure
├── cloudformation/
│   └── template.yaml          # CloudFormation template
├── scripts/
│   ├── deploy.sh              # One-click deployment
│   └── destroy.sh             # Cleanup script
├── assets/                    # Generated during deployment
│   ├── dashboard_main.zip
│   └── dashboard_recommendations.zip
└── README.md                  # This file
```

## 🔒 **Security**

### **IAM Permissions**
- **Minimal permissions** → Only Lambda execution rights
- **No persistent storage** → Stateless architecture
- **Public endpoints** → Function URLs with CORS
- **No secrets** → All configuration in code

### **Network Security**
- **HTTPS only** → All traffic encrypted
- **CORS enabled** → Cross-origin requests allowed
- **No VPC** → Public internet access
- **Serverless** → No infrastructure to manage

## 💰 **Cost Estimation**

### **AWS Free Tier Eligible**
- **Lambda requests** → 1M free per month
- **Lambda compute** → 400,000 GB-seconds free
- **Estimated cost** → $0/month for typical usage

### **Beyond Free Tier**
- **Lambda requests** → $0.20 per 1M requests
- **Lambda compute** → $0.0000166667 per GB-second
- **Estimated cost** → <$1/month for moderate usage

## 🚀 **Production Considerations**

### **Enhancements for Production**
1. **Custom Domain** → Route 53 + CloudFront
2. **Authentication** → Cognito or IAM
3. **Monitoring** → CloudWatch dashboards
4. **CI/CD** → GitHub Actions deployment
5. **Environment Management** → Dev/Staging/Prod stacks

### **Scaling**
- **Auto-scaling** → Lambda handles traffic spikes
- **Global deployment** → Multi-region support
- **CDN integration** → CloudFront for performance
- **Database integration** → DynamoDB for persistence

## 🐛 **Troubleshooting**

### **Common Issues**

**AWS CLI not configured:**
```bash
aws configure
# Enter your AWS Access Key ID, Secret, Region, and Output format
```

**Insufficient permissions:**
```bash
# Ensure your AWS user has these permissions:
# - CloudFormation full access
# - Lambda full access
# - IAM role creation
```

**Stack already exists:**
```bash
# Delete existing stack first
./scripts/destroy.sh
# Then redeploy
./scripts/deploy.sh
```

### **Logs and Debugging**
```bash
# View CloudFormation events
aws cloudformation describe-stack-events --stack-name agentcore-security-dashboard-stack

# View Lambda logs
aws logs describe-log-groups --log-group-name-prefix /aws/lambda/agentcore-security-dashboard
```

## 📞 **Support**

- **Repository**: https://github.com/ajitnk-lab/agenticaihackathon
- **Issues**: Create GitHub issue for bugs/questions
- **Documentation**: See main README.md and ARCHITECTURE.md

---

**Ready to deploy?** Run `./scripts/deploy.sh` and your AgentCore Security Dashboard will be live in minutes! 🚀
