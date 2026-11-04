"""Regression guards for the migration's externally important security boundary."""
import importlib.util
from pathlib import Path


spec = importlib.util.spec_from_file_location('ec2_template', Path(__file__).parents[1] / 'tools/render_private_ec2.py')
template_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(template_module)


def test_no_public_inbound_listener_or_ssh_key():
    resources = template_module.build()['Resources']
    assert resources['PrivateSecurityGroup']['Properties']['SecurityGroupIngress'] == []
    instance = resources['Server']['Properties']
    assert 'KeyName' not in instance
    bootstrap = instance['UserData']['Fn::Base64']['Fn::Sub']
    assert '--host=127.0.0.1 --port=8000' in bootstrap
    assert '--host=0.0.0.0' not in bootstrap


def test_imds_v2_and_encrypted_small_disk_with_standard_credits():
    instance = template_module.build()['Resources']['Server']['Properties']
    assert instance['InstanceType'] == 't4g.micro'
    assert instance['MetadataOptions']['HttpTokens'] == 'required'
    disk = instance['BlockDeviceMappings'][0]['Ebs']
    assert disk['Encrypted'] is True and disk['VolumeSize'] == 8
    assert instance['CreditSpecification']['CPUCredits'] == 'standard'


def test_collaborators_cannot_grant_roles_or_manage_other_instances():
    resources = template_module.build()['Resources']
    statements = resources['Administrators']['Properties']['Policies'][0]['PolicyDocument']['Statement']
    all_actions = [action for s in statements for action in
                   (s['Action'] if isinstance(s['Action'], list) else [s['Action']])]
    assert not any(action in all_actions for action in ('iam:*', 'ec2:*', 'iam:PassRole', 'ssm:SendCommand'))
    for statement in statements:
        if 'ec2:StopInstances' in statement['Action']:
            assert statement['Resource']['Fn::Sub'].endswith('instance/${Server}')


def test_login_passwords_are_not_in_the_template():
    template = template_module.build()
    for name in ('One', 'Two'):
        user = template['Resources']['Administrator' + name]['Properties']
        assert 'LoginProfile' not in user
        parameter = template['Parameters']['AdminUser' + name]
        assert parameter['NoEcho'] is True and 'Default' not in parameter
