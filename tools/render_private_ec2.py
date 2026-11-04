"""Render the reviewable, secret-free FRY-59 CloudFormation template."""
from pathlib import Path
import json


def sub(value):
    return {'Fn::Sub': value}


def ref(value):
    return {'Ref': value}


def build():
    bootstrap = (Path(__file__).resolve().parents[1] / 'infra/private-ec2-bootstrap.sh').read_text(encoding='utf8')
    bootstrap = bootstrap.replace('${', '${!').replace('__ADMIN_ONE__', '${AdminUserOne}').replace('__ADMIN_TWO__', '${AdminUserTwo}')
    instance_arn = sub('arn:${AWS::Partition}:ec2:${AWS::Region}:${AWS::AccountId}:instance/${Server}')
    document_arn = sub('arn:${AWS::Partition}:ssm:${AWS::Region}:${AWS::AccountId}:document/${AdminSession}')
    forward_arn = sub('arn:${AWS::Partition}:ssm:${AWS::Region}::document/AWS-StartPortForwardingSession')
    user_arn = sub('arn:${AWS::Partition}:iam::${AWS::AccountId}:user/${!aws:username}')
    permissions = [
        {'Effect': 'Allow', 'Action': ['ec2:DescribeInstances', 'ec2:DescribeInstanceStatus',
            'ec2:DescribeTags', 'ssm:DescribeInstanceInformation', 'ssm:DescribeInstanceProperties',
            'ssm:DescribeSessions', 'ssm:GetConnectionStatus'], 'Resource': '*'},
        {'Effect': 'Allow', 'Action': ['ec2:StartInstances', 'ec2:StopInstances', 'ec2:RebootInstances'],
            'Resource': instance_arn},
        {'Effect': 'Allow', 'Action': 'ssm:StartSession', 'Resource': [instance_arn, document_arn, forward_arn]},
        {'Effect': 'Allow', 'Action': ['ssm:GetDocument', 'ssm:DescribeDocument'], 'Resource': [document_arn, forward_arn]},
        {'Effect': 'Allow', 'Action': ['ssm:TerminateSession', 'ssm:ResumeSession'],
            'Resource': sub('arn:${AWS::Partition}:ssm:${AWS::Region}:${AWS::AccountId}:session/${!aws:username}-*')},
        {'Effect': 'Allow', 'Action': ['iam:ChangePassword', 'iam:GetUser', 'iam:ListMFADevices',
            'iam:EnableMFADevice', 'iam:ResyncMFADevice'], 'Resource': user_arn},
        {'Effect': 'Allow', 'Action': 'iam:CreateVirtualMFADevice',
            'Resource': sub('arn:${AWS::Partition}:iam::${AWS::AccountId}:mfa/${!aws:username}')},
        {'Effect': 'Allow', 'Action': 'iam:GetAccountPasswordPolicy', 'Resource': '*'},
    ]
    resources = {
        'ServerRole': {'Type': 'AWS::IAM::Role', 'Properties': {
            'AssumeRolePolicyDocument': {'Version': '2012-10-17', 'Statement': [{
                'Effect': 'Allow', 'Principal': {'Service': 'ec2.amazonaws.com'}, 'Action': 'sts:AssumeRole'}]},
            'ManagedPolicyArns': [sub('arn:${AWS::Partition}:iam::aws:policy/AmazonSSMManagedInstanceCore')]}},
        'ServerProfile': {'Type': 'AWS::IAM::InstanceProfile', 'Properties': {'Roles': [ref('ServerRole')]}},
        'PrivateSecurityGroup': {'Type': 'AWS::EC2::SecurityGroup', 'Properties': {
            'GroupDescription': 'Fry private development: no inbound access; authenticated SSM only',
            'VpcId': ref('VpcId'), 'SecurityGroupIngress': [],
            'SecurityGroupEgress': [{'IpProtocol': '-1', 'CidrIp': '0.0.0.0/0'}],
            'Tags': [{'Key': 'Project', 'Value': 'Fry'}, {'Key': 'Name', 'Value': 'Fry-private-no-ingress'}]}},
        'Server': {'Type': 'AWS::EC2::Instance', 'Properties': {
            'ImageId': ref('ImageId'), 'InstanceType': 't4g.micro',
            'IamInstanceProfile': ref('ServerProfile'),
            'NetworkInterfaces': [{'DeviceIndex': '0', 'SubnetId': ref('SubnetId'),
                'AssociatePublicIpAddress': False, 'GroupSet': [ref('PrivateSecurityGroup')]}],
            'BlockDeviceMappings': [{'DeviceName': '/dev/xvda', 'Ebs': {
                'VolumeType': 'gp3', 'VolumeSize': 8, 'Encrypted': True, 'DeleteOnTermination': True}}],
            'CreditSpecification': {'CPUCredits': 'standard'},
            'MetadataOptions': {'HttpEndpoint': 'enabled', 'HttpTokens': 'required', 'HttpPutResponseHopLimit': 1},
            'UserData': {'Fn::Base64': sub(bootstrap)},
            'Tags': [{'Key': 'Project', 'Value': 'Fry'}, {'Key': 'Name', 'Value': 'Fry-private-dev'}]}},
        'OutboundAddress': {'Type': 'AWS::EC2::EIP', 'Properties': {'Domain': 'vpc',
            'Tags': [{'Key': 'Project', 'Value': 'Fry'}, {'Key': 'Name', 'Value': 'Fry-Google-outbound'}]}},
        'OutboundAssociation': {'Type': 'AWS::EC2::EIPAssociation', 'Properties': {
            'AllocationId': {'Fn::GetAtt': ['OutboundAddress', 'AllocationId']}, 'InstanceId': ref('Server')}},
        'AdminSession': {'Type': 'AWS::SSM::Document', 'Properties': {
            'DocumentType': 'Session', 'DocumentFormat': 'JSON', 'Name': 'Fry-AdminShell',
            'Content': {'schemaVersion': '1.0', 'description': 'Private Fry administrative shell using the signed-in identity',
                'sessionType': 'Standard_Stream', 'inputs': {
                    's3BucketName': '', 's3KeyPrefix': '', 's3EncryptionEnabled': True,
                    'cloudWatchLogGroupName': '', 'cloudWatchEncryptionEnabled': True,
                    'cloudWatchStreamingEnabled': False, 'kmsKeyId': '',
                    'runAsEnabled': True, 'runAsDefaultUser': '',
                    'idleSessionTimeout': '20', 'maxSessionDuration': '60',
                    'shellProfile': {'windows': '', 'linux': 'cd /srv/ratemyfries; exec /bin/bash'}}}}},
        'Administrators': {'Type': 'AWS::IAM::Group', 'Properties': {
            'ManagedPolicyArns': [sub('arn:${AWS::Partition}:iam::aws:policy/SignInLocalDevelopmentAccess')],
            'Policies': [{
            'PolicyName': 'FryServerAdministration', 'PolicyDocument': {'Version': '2012-10-17', 'Statement': permissions}}]}},
    }
    for suffix, parameter in [('One', 'AdminUserOne'), ('Two', 'AdminUserTwo')]:
        resources['Administrator' + suffix] = {'Type': 'AWS::IAM::User', 'Properties': {
            'UserName': ref(parameter), 'Groups': [ref('Administrators')],
            'Tags': [{'Key': 'SSMSessionRunAs', 'Value': ref(parameter)}, {'Key': 'Project', 'Value': 'Fry'}]}}
    return {
        'AWSTemplateFormatVersion': '2010-09-09',
        'Description': 'FRY-59 private class development instance; website is available only through authenticated SSM forwarding.',
        'Parameters': {
            'VpcId': {'Type': 'AWS::EC2::VPC::Id'}, 'SubnetId': {'Type': 'AWS::EC2::Subnet::Id'},
            'ImageId': {'Type': 'AWS::SSM::Parameter::Value<AWS::EC2::Image::Id>',
                'Default': '/aws/service/ami-amazon-linux-latest/al2023-ami-kernel-default-arm64'},
            'AdminUserOne': {'Type': 'String', 'NoEcho': True, 'AllowedPattern': '[A-Za-z][A-Za-z0-9_]{1,30}'},
            'AdminUserTwo': {'Type': 'String', 'NoEcho': True, 'AllowedPattern': '[A-Za-z][A-Za-z0-9_]{1,30}'},
        },
        'Resources': resources,
        'Outputs': {'InstanceId': {'Value': ref('Server')},
            'OutboundIPv4': {'Value': ref('OutboundAddress')},
            'AdminSessionDocument': {'Value': ref('AdminSession')},
            'Connection': {'Value': 'Authenticated AWS Session Manager only; no public website or inbound ports'}},
    }


if __name__ == '__main__':
    target = Path(__file__).resolve().parents[1] / 'infra/private-ec2.template.json'
    target.write_text(json.dumps(build(), indent=2) + '\n', encoding='utf8')
    print('Rendered', target.name)
