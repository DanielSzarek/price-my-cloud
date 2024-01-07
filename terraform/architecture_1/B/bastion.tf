resource "aws_security_group" "allow_ssh" {
  name        = "allow_ssh"
  description = "Allow ssh inbound traffic"

  # using default VPC
  vpc_id      = aws_vpc.vpc.id

  ingress {
    description = "HTTP from VPC"

    # we should allow incoming and outoging
    # TCP packets
    protocol = "tcp"
    from_port = 0
    to_port = 80

    # allow all traffic
    cidr_blocks = ["10.0.0.0/16"]
  }

  ingress {
    description = "ICMP from VPC"

    # we should allow incoming and outoging
    # TCP packets
    from_port = -1
    to_port = -1
    protocol = "icmp"

    # allow all traffic
    cidr_blocks = ["10.0.0.0/16"]
  }

  ingress {
    description = "TLS from VPC"

    # we should allow incoming and outoging
    # TCP packets
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"

    # allow all traffic
    cidr_blocks = ["0.0.0.0/0"]
  }


  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "allow_ssh"
  }
}

resource "aws_security_group" "postgresql" {
  name        = "postgresql"
  description = "Allow postgresql inbound traffic"

  # using default VPC
  vpc_id      = aws_vpc.vpc.id

  # Allow inbound traffic on port 5432 from all sources
  ingress {
    from_port = 5432
    to_port   = 5432
    protocol  = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Allow outbound traffic to all destinations on all ports
  egress {
    from_port = 0
    to_port   = 0
    protocol  = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_key_pair" "key" {
  key_name   = "poc-key"
  public_key = tls_private_key.priv.public_key_openssh
}

resource "tls_private_key" "priv" {
  algorithm = "RSA"
  rsa_bits = 4096
}

resource "local_file" "key" {
  content = tls_private_key.priv.private_key_pem
  filename = "${path.module}/poc-key.pem"
  file_permission = "0400"
}

data "aws_ami" "ubuntu" {
  most_recent = true

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-focal-20.04-amd64-server-*"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }

  owners = ["099720109477"] # Canonical
}

resource "aws_instance" "bastion" {
  ami             = data.aws_ami.ubuntu.id
  instance_type   = "t2.micro"

  key_name        = aws_key_pair.key.key_name
  subnet_id = aws_subnet.pub-subnet-1.id
  vpc_security_group_ids = [aws_security_group.allow_ssh.id]

  user_data = <<EOF
#!/bin/bash
echo "${tls_private_key.priv.private_key_pem}" > /home/ubuntu/poc-key.pem
chown ubuntu:ubuntu /home/ubuntu/poc-key.pem
chmod 400 /home/ubuntu/poc-key.pem
EOF
}

output "connection_string" {
  value = "ssh -i ${aws_key_pair.key.key_name}.pem ubuntu@${aws_instance.bastion.public_ip}"
  description = "The IP of bastion host to connect to."
}
