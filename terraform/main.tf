terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
  }

  required_version = ">= 1.5.0"
}

provider "aws" {
  region = "ap-south-1"
}

# Security Group
resource "aws_security_group" "analytics_sg" {
  name        = "ai-analytics-sg"
  description = "Security group for AI Analytics Dashboard"

  # SSH access for Ansible
  ingress {
    description = "SSH"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Streamlit application
  ingress {
    description = "Streamlit"
    from_port   = 8501
    to_port     = 8501
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Allow outbound traffic
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# Ubuntu EC2 instance
resource "aws_instance" "analytics_server" {
  ami           = "ami-0f918f7e67a3323f0"
  instance_type = "t3.micro"

  key_name = "fa1-key"

  vpc_security_group_ids = [
    aws_security_group.analytics_sg.id
  ]

  tags = {
    Name = "AI-Analytics-Server"
  }
}

# Display EC2 public IP
output "public_ip" {
  value = aws_instance.analytics_server.public_ip
}