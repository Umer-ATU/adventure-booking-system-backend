# ──────────────────────────────────────────────
# Outputs
# ──────────────────────────────────────────────

output "ec2_public_ip" {
  description = "Public IP of the backend EC2 instance"
  value       = aws_eip.backend.public_ip
}

output "backend_url" {
  description = "Backend API URL"
  # If an API custom domain is provided, output that. Else output the EC2 IP.
  value       = var.api_custom_domain_name != "" ? "https://${var.api_custom_domain_name}/api" : "http://${aws_eip.backend.public_ip}:8000"
}

output "backend_docs_url" {
  description = "Backend Swagger docs URL"
  value       = var.api_custom_domain_name != "" ? "https://${var.api_custom_domain_name}/docs" : "http://${aws_eip.backend.public_ip}:8000/docs"
}

output "s3_bucket_name" {
  description = "S3 bucket name for frontend"
  value       = aws_s3_bucket.frontend.id
}

output "s3_website_url" {
  description = "S3 static website URL"
  value       = "http://${aws_s3_bucket_website_configuration.frontend.website_endpoint}"
}

output "cloudfront_domain" {
  description = "CloudFront distribution domain (your frontend URL)"
  value       = var.custom_domain_name != "" ? "https://${var.custom_domain_name}" : "https://${aws_cloudfront_distribution.frontend.domain_name}"
}

output "cloudfront_default_domain" {
  description = "The default CloudFront distribution domain (useful for testing or DNS aliases)"
  value       = aws_cloudfront_distribution.frontend.domain_name
}

output "cloudfront_distribution_id" {
  description = "CloudFront distribution ID (needed for cache invalidation)"
  value       = aws_cloudfront_distribution.frontend.id
}

output "ssh_command" {
  description = "SSH command to connect to EC2"
  value       = "ssh -i /path/to/your/private-key-file.pem ec2-user@${aws_eip.backend.public_ip}"
}

output "frontend_deploy_command" {
  description = "Command to deploy frontend (run from frontend repo root after npm run build)"
  value       = "aws s3 sync dist/ s3://${aws_s3_bucket.frontend.id} --delete && aws cloudfront create-invalidation --distribution-id ${aws_cloudfront_distribution.frontend.id} --paths '/*'"
}

output "ecr_repository_url" {
  description = "URL of the ECR repository"
  value       = aws_ecr_repository.backend.repository_url
}
