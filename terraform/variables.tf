# ──────────────────────────────────────────────
# General
# ──────────────────────────────────────────────
variable "aws_region" {
  description = "AWS region to deploy into"
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Project name used for resource naming"
  type        = string
  default     = "helena"
}

variable "environment" {
  description = "Deployment environment (e.g. production, staging)"
  type        = string
  default     = "production"
}


# ──────────────────────────────────────────────
# EC2 / Backend
# ──────────────────────────────────────────────
variable "instance_type" {
  description = "EC2 instance type"
  type        = string
  default     = "t2.micro"
}

variable "public_key" {
  description = "Public SSH key for EC2 instance access"
  type        = string
}

variable "ssh_allowed_cidr" {
  description = "CIDR block allowed to SSH (use your IP, e.g. 1.2.3.4/32)"
  type        = string
  default     = "0.0.0.0/0"
}

variable "backend_repo_url" {
  description = "HTTPS URL of the backend Git repository"
  type        = string
}

# ──────────────────────────────────────────────
# Backend Environment Variables
# ──────────────────────────────────────────────
variable "mongodb_url" {
  description = "MongoDB connection string"
  type        = string
  sensitive   = true
}

variable "database_name" {
  description = "MongoDB database name"
  type        = string
  default     = "booking_system"
}

variable "secret_key" {
  description = "JWT secret key (generate with: openssl rand -hex 32)"
  type        = string
  sensitive   = true
}

variable "stripe_secret_key" {
  description = "Stripe secret key"
  type        = string
  sensitive   = true
}

variable "stripe_publishable_key" {
  description = "Stripe publishable key"
  type        = string
  sensitive   = true
}

variable "stripe_webhook_secret" {
  description = "Stripe webhook secret"
  type        = string
  sensitive   = true
}

# ──────────────────────────────────────────────
# Frontend / S3
# ──────────────────────────────────────────────
variable "frontend_bucket_name" {
  description = "S3 bucket name for frontend (must be globally unique)"
  type        = string
  default     = "helena-adventure-frontend"
}

# ──────────────────────────────────────────────
# Custom Domain (Optional)
# ──────────────────────────────────────────────
variable "custom_domain_name" {
  description = "Custom domain name (e.g. helena.umer-karachiwala.xyz). Leave empty to use default CloudFront domain."
  type        = string
  default     = ""
}

variable "api_custom_domain_name" {
  description = "Custom domain name for the backend API (e.g. api.adventure.umer-karachiwala.com). Leave empty to use default CloudFront domain."
  type        = string
  default     = ""
}

variable "acm_certificate_arn" {
  description = "ARN of the ACM certificate for the custom domain (must be in us-east-1). Required if custom_domain_name is provided."
  type        = string
  default     = ""
}
