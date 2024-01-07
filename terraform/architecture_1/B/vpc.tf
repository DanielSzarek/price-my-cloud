resource "aws_vpc" "vpc" {
    cidr_block = "10.0.0.0/16"

	tags = {
		Name = "POC-VPC"
	}
}

resource "aws_subnet" "pub-subnet-1" {
	vpc_id = aws_vpc.vpc.id
	cidr_block = "10.0.0.0/24"
	availability_zone = "us-west-2a"

	map_public_ip_on_launch = true

	tags = {
		Name = "POC-PUBSUB-1"
	}
}

resource "aws_subnet" "subnet-1" {
	vpc_id = aws_vpc.vpc.id
	cidr_block = "10.0.1.0/24"
	availability_zone = "us-west-2b"

	tags = {
		Name = "POC-SUB-1"
	}
}

resource "aws_internet_gateway" "igtw" {
  vpc_id = aws_vpc.vpc.id
  tags = {
    Name = "POC-IGTW"
  }
}

resource "aws_route_table" "pub-route-table" {
  vpc_id = aws_vpc.vpc.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.igtw.id
  }

  tags = {
	Name = "POC-PUB-RT"
  }
}

resource "aws_route_table_association" "pub-route-table-association" {
  subnet_id      = aws_subnet.pub-subnet-1.id
  route_table_id = aws_route_table.pub-route-table.id
}

resource "aws_eip" "eip" {
  vpc              = true
  public_ipv4_pool = "amazon"
}

resource "aws_nat_gateway" "natgtw" {
  allocation_id = aws_eip.eip.id
  subnet_id     = aws_subnet.pub-subnet-1.id

  tags = {
    Name = "POC-NATGTW"
  }
}

resource "aws_route_table" "private-subnet-route-table" {
  vpc_id = aws_vpc.vpc.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_nat_gateway.natgtw.id
  }

  tags = {
    Name = "POC-RT"
  }
}

resource "aws_route_table_association" "priv-route-table-association" {
  subnet_id      = aws_subnet.subnet-1.id
  route_table_id = aws_route_table.private-subnet-route-table.id
}

output "nat-gateway" {
	value = "${aws_nat_gateway.natgtw.private_ip}"
}
