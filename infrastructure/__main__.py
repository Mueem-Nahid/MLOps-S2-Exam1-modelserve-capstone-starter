import os
import pulumi
import pulumi_aws as aws

PREFIX = "modelserve"
SSH_PUBLIC_KEY = os.environ.get("SSH_PUBLIC_KEY", "")

vpc = aws.ec2.Vpc(
    f"{PREFIX}-vpc",
    cidr_block="10.0.0.0/16",
    tags={"Name": f"{PREFIX}-vpc", "Project": "modelserve"},
)

igw = aws.ec2.InternetGateway(
    f"{PREFIX}-igw",
    vpc_id=vpc.id,
    tags={"Name": f"{PREFIX}-igw", "Project": "modelserve"},
)

subnet = aws.ec2.Subnet(
    f"{PREFIX}-subnet",
    vpc_id=vpc.id,
    cidr_block="10.0.1.0/24",
    map_public_ip_on_launch=True,
    tags={"Name": f"{PREFIX}-subnet", "Project": "modelserve"},
)

route_table = aws.ec2.RouteTable(
    f"{PREFIX}-rt",
    vpc_id=vpc.id,
    routes=[
        aws.ec2.RouteTableRouteArgs(
            cidr_block="0.0.0.0/0",
            gateway_id=igw.id,
        )
    ],
    tags={"Name": f"{PREFIX}-rt", "Project": "modelserve"},
)

aws.ec2.RouteTableAssociation(
    f"{PREFIX}-rt-assoc",
    subnet_id=subnet.id,
    route_table_id=route_table.id,
)

sg = aws.ec2.SecurityGroup(
    f"{PREFIX}-sg",
    vpc_id=vpc.id,
    ingress=[
        aws.ec2.SecurityGroupIngressArgs(
            protocol="tcp",
            from_port=22,
            to_port=22,
            cidr_blocks=["0.0.0.0/0"],
            description="SSH",
        ),
        aws.ec2.SecurityGroupIngressArgs(
            protocol="tcp",
            from_port=8000,
            to_port=8000,
            cidr_blocks=["0.0.0.0/0"],
            description="FastAPI",
        ),
        aws.ec2.SecurityGroupIngressArgs(
            protocol="tcp",
            from_port=3000,
            to_port=3000,
            cidr_blocks=["0.0.0.0/0"],
            description="Grafana",
        ),
        aws.ec2.SecurityGroupIngressArgs(
            protocol="tcp",
            from_port=5000,
            to_port=5000,
            cidr_blocks=["0.0.0.0/0"],
            description="MLflow",
        ),
        aws.ec2.SecurityGroupIngressArgs(
            protocol="tcp",
            from_port=9090,
            to_port=9090,
            cidr_blocks=["0.0.0.0/0"],
            description="Prometheus",
        ),
    ],
    egress=[
        aws.ec2.SecurityGroupEgressArgs(
            protocol="-1",
            from_port=0,
            to_port=0,
            cidr_blocks=["0.0.0.0/0"],
            description="All outbound",
        )
    ],
    tags={"Name": f"{PREFIX}-sg", "Project": "modelserve"},
)

iam_role = aws.iam.Role(
    f"{PREFIX}-instance-role",
    assume_role_policy="""{
        "Version": "2012-10-17",
        "Statement": [{
            "Effect": "Allow",
            "Principal": {"Service": "ec2.amazonaws.com"},
            "Action": "sts:AssumeRole"
        }]
    }""",
    tags={"Project": "modelserve"},
)

aws.iam.RolePolicyAttachment(
    f"{PREFIX}-s3-readwrite",
    role=iam_role.name,
    policy_arn="arn:aws:iam::aws:policy/AmazonS3FullAccess",
)

aws.iam.RolePolicyAttachment(
    f"{PREFIX}-ecr-pull",
    role=iam_role.name,
    policy_arn="arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly",
)

instance_profile = aws.iam.InstanceProfile(
    f"{PREFIX}-instance-profile",
    role=iam_role.name,
)

ec2 = aws.ec2.Instance(
    f"{PREFIX}-ec2",
    ami="ami-0c55b159cbfafe1f0",
    instance_type="t3.small",
    subnet_id=subnet.id,
    vpc_security_group_ids=[sg.id],
    iam_instance_profile=instance_profile.name,
    key_name=PREFIX if SSH_PUBLIC_KEY else "",
    user_data="""#!/bin/bash
yum update -y
yum install -y docker
usermod -aG docker ec2-user
systemctl start docker
systemctl enable docker
pip3 install docker-compose
""",
    tags={"Name": f"{PREFIX}-ec2", "Project": "modelserve"},
)

ecr = aws.ecr.Repository(
    f"{PREFIX}-ecr",
    force_delete=True,
    tags={"Project": "modelserve"},
)

s3_bucket = aws.s3.Bucket(
    f"{PREFIX}-mlflow",
    bucket=f"{PREFIX}-mlflow-artifacts",
    tags={"Name": f"{PREFIX}-mlflow", "Project": "modelserve"},
)

pulumi.export("vpc_id", vpc.id)
pulumi.export("subnet_id", subnet.id)
pulumi.export("security_group_id", sg.id)
pulumi.export("ec2_public_ip", ec2.public_ip)
pulumi.export("ecr_repo_url", ecr.repository_url)
pulumi.export("s3_bucket_name", s3_bucket.id)