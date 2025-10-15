terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# Variables
variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Project name"
  type        = string
  default     = "agentcore-security-dashboard"
}

# IAM Role for Lambda
resource "aws_iam_role" "lambda_execution_role" {
  name = "${var.project_name}-lambda-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_basic_execution" {
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
  role       = aws_iam_role.lambda_execution_role.name
}

# Lambda function for main dashboard
resource "aws_lambda_function" "dashboard_main" {
  filename         = "../assets/dashboard_main.zip"
  function_name    = "${var.project_name}-main"
  role            = aws_iam_role.lambda_execution_role.arn
  handler         = "lambda_function.lambda_handler"
  runtime         = "python3.9"
  timeout         = 30

  depends_on = [aws_iam_role_policy_attachment.lambda_basic_execution]
}

# Lambda function for recommendations
resource "aws_lambda_function" "dashboard_recommendations" {
  filename         = "../assets/dashboard_recommendations.zip"
  function_name    = "${var.project_name}-recommendations"
  role            = aws_iam_role.lambda_execution_role.arn
  handler         = "lambda_function.lambda_handler"
  runtime         = "python3.9"
  timeout         = 30

  depends_on = [aws_iam_role_policy_attachment.lambda_basic_execution]
}

# Function URLs
resource "aws_lambda_function_url" "dashboard_main_url" {
  function_name      = aws_lambda_function.dashboard_main.function_name
  authorization_type = "NONE"

  cors {
    allow_credentials = false
    allow_origins     = ["*"]
    allow_methods     = ["GET", "POST"]
    allow_headers     = ["date", "keep-alive"]
    expose_headers    = ["date", "keep-alive"]
    max_age          = 86400
  }
}

resource "aws_lambda_function_url" "dashboard_recommendations_url" {
  function_name      = aws_lambda_function.dashboard_recommendations.function_name
  authorization_type = "NONE"

  cors {
    allow_credentials = false
    allow_origins     = ["*"]
    allow_methods     = ["GET", "POST"]
    allow_headers     = ["date", "keep-alive"]
    expose_headers    = ["date", "keep-alive"]
    max_age          = 86400
  }
}

# Outputs
output "main_dashboard_url" {
  description = "URL for the main dashboard"
  value       = aws_lambda_function_url.dashboard_main_url.function_url
}

output "recommendations_url" {
  description = "URL for the recommendations page"
  value       = aws_lambda_function_url.dashboard_recommendations_url.function_url
}

output "lambda_role_arn" {
  description = "ARN of the Lambda execution role"
  value       = aws_iam_role.lambda_execution_role.arn
}
