# DB
resource "aws_instance" "postgresql-server-1" {
  ami           = data.aws_ami.ubuntu.id
  instance_type = "t2.micro"
  key_name      = aws_key_pair.key.key_name

  vpc_security_group_ids = [aws_security_group.allow_ssh.id, aws_security_group.postgresql.id]
  subnet_id              = aws_subnet.subnet-1.id

  tags = {
    Name = "postgresql"
  }

  user_data = <<-EOF
              #!/bin/bash
              sudo apt-get update &&
              sudo apt-get install -y postgresql postgresql-contrib &&
              sudo git clone https://github.com/DanielSzarek/price-my-cloud.git &&
              git config --global --add safe.directory /price-my-cloud &&
              cd /price-my-cloud/ &&
              sudo git checkout feature/3-create-micro-system-mock &&
              cd micro-system-mock &&
              bash create_database.sh
              EOF
}

output "postgresql-server-1" {
  value = "${aws_instance.postgresql-server-1.private_ip}"
  description = "The IP of postgresql server."
}

# ==================================================================

# export RANGE_FROM=5_000_000
# export RANGE_TO=25_000_000
resource "aws_instance" "server-2" {
  ami             = data.aws_ami.ubuntu.id
  instance_type   = "t2.micro"
  key_name        = aws_key_pair.key.key_name

  subnet_id = aws_subnet.subnet-1.id
  vpc_security_group_ids = [aws_security_group.allow_ssh.id, aws_security_group.postgresql.id]

  user_data = <<-EOF
              #!/bin/bash
              sudo apt-get update -y &&
              curl -sSL https://install.python-poetry.org | python3 - &&
              sudo git clone https://github.com/DanielSzarek/price-my-cloud.git &&
              sudo git config --global --add safe.directory /price-my-cloud &&
              cd /price-my-cloud/ &&
              sudo git checkout feature/3-create-micro-system-mock &&
              cd micro-system-mock &&
              sudo /home/ubuntu/.local/bin/poetry update &&
              sudo /home/ubuntu/.local/bin/poetry run uvicorn micro_system_mock.main:app --host 0.0.0.0 --port 80
              EOF
}

output "server-2" {
  value = "${aws_instance.server-2.private_ip}"
  description = "The IP of server-2."
}

# ==================================================================

# export RANGE_FROM=5_000_000
# export RANGE_TO=25_000_000
resource "aws_instance" "server-2-2" {
  ami             = data.aws_ami.ubuntu.id
  instance_type   = "t2.micro"
  key_name        = aws_key_pair.key.key_name

  subnet_id = aws_subnet.subnet-1.id
  vpc_security_group_ids = [aws_security_group.allow_ssh.id, aws_security_group.postgresql.id]

  user_data = <<-EOF
              #!/bin/bash
              sudo apt-get update -y &&
              curl -sSL https://install.python-poetry.org | python3 - &&
              sudo git clone https://github.com/DanielSzarek/price-my-cloud.git &&
              sudo git config --global --add safe.directory /price-my-cloud &&
              cd /price-my-cloud/ &&
              sudo git checkout feature/3-create-micro-system-mock &&
              cd micro-system-mock &&
              sudo /home/ubuntu/.local/bin/poetry update &&
              sudo -E /home/ubuntu/.local/bin/poetry run uvicorn micro_system_mock.main:app --host 0.0.0.0 --port 80
              EOF
}

output "server-2-2" {
  value = "${aws_instance.server-2-2.private_ip}"
  description = "The IP of server-2-2."
}


# ==================================================================

resource "aws_instance" "server-1" {
  ami             = data.aws_ami.ubuntu.id
  instance_type   = "t2.micro"
  key_name        = aws_key_pair.key.key_name

  subnet_id = aws_subnet.subnet-1.id
  vpc_security_group_ids = [aws_security_group.allow_ssh.id]

  export API_ENDPOINTS="http://${aws_instance.server-2.private_ip}/"
  export SHOULD_CALL_APIS=true &&
  export DB_CONNECTION_STRING="postgresql://postgres:postgres@${aws_instance.postgresql-server-1.private_ip}/testdb"
  export SHOULD_CALL_DB=true
  user_data = <<-EOF
            #!/bin/bash
            sudo apt update -y &&
            curl -sSL https://install.python-poetry.org | python3 - &&
            sudo git clone https://github.com/DanielSzarek/price-my-cloud.git &&
            sudo git config --global --add safe.directory /price-my-cloud &&
            cd /price-my-cloud/ &&
            sudo git checkout feature/3-create-micro-system-mock &&
            cd micro-system-mock &&
            sudo -E /home/ubuntu/.local/bin/poetry update &&
            sudo -E /home/ubuntu/.local/bin/poetry run uvicorn micro_system_mock.main:app --host 0.0.0.0 --port 80
            EOF
}

output "server-1" {
  value = "${aws_instance.server-1.private_ip}"
  description = "The IP of server-1."
}

# ==================================================================

resource "aws_instance" "load-balancer-mock" {
  ami             = data.aws_ami.ubuntu.id
  instance_type   = "t2.micro"
  key_name        = aws_key_pair.key.key_name

  subnet_id = aws_subnet.subnet-1.id
  vpc_security_group_ids = [aws_security_group.allow_ssh.id]

  TODO add auto run
  export API_ENDPOINTS="http://${aws_instance.server-1.private_ip}/"
  export SLEEP_TIME=1 &&
  user_data = <<-EOF
              #!/bin/bash
              sudo apt update -y &&
              sudo apt-get -y install python3-pip &&
              pip3 install aiohttp &&
              sudo git clone https://github.com/DanielSzarek/price-my-cloud.git &&
              sudo git config --global --add safe.directory /price-my-cloud &&
              cd /price-my-cloud/ &&
              sudo git checkout feature/3-create-micro-system-mock &&
              cd load-balancer-mock/
              EOF
}

output "load-balancer-mock" {
  value = "${aws_instance.load-balancer-mock.private_ip}"
  description = "The IP of load-balancer-mock."
}
