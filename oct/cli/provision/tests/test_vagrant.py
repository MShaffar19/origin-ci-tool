# coding=utf-8
from __future__ import absolute_import, division, print_function

from mock import patch
from oct.cli.provision import vagrant
from oct.cli.provision.vagrant import DEFAULT_MASTER_IP, OperatingSystem, Provider, Stage
from oct.config import vagrant as vagrant_configuration
from oct.config.configuration import Configuration, DEFAULT_HOSTNAME
from oct.config.vagrant import VagrantVMMetadata
from oct.tests.unit.playbook_runner_test_case import CLICK_RC_USAGE, PlaybookRunnerTestCase, TestCaseParameters, show_stack_trace

_vagrant_root = '/vagrant'
_default_home_dir = _vagrant_root + '/' + DEFAULT_HOSTNAME

if not show_stack_trace:
    __unittest = True


class ProvisionVagrantTestCase(PlaybookRunnerTestCase):
    def setUp(self):
        PlaybookRunnerTestCase.setUp(self)
        patches = [
            patch.object(
                target=VagrantVMMetadata,
                attribute='load',
                new=lambda _, __: None
            ),
            patch.object(
                target=VagrantVMMetadata,
                attribute='write',
                new=lambda _: None
            ),
            patch.object(
                target=VagrantVMMetadata,
                attribute='remove',
                new=lambda _: None
            ),
            patch.object(
                target=Configuration,
                attribute='vagrant_directory_root',
                new='/vagrant'
            ),
            patch.object(
                target=Configuration,
                attribute='_vagrant_hostname_taken',
                new=lambda _, __: False
            ),
            patch.object(
                target=vagrant,
                attribute='register_host',
                new=lambda _, __, ___, ____, _____, ______: None
            ),
            patch.object(
                target=vagrant_configuration,
                attribute='fetch_ssh_configuration',
                new=lambda _, __: {
                    'hostname': DEFAULT_HOSTNAME,
                    'host': DEFAULT_MASTER_IP,
                    'port': 22,
                    'identityfile': 'unimportant',
                    'user': 'vagrant'
                }
            )
        ]
        for patcher in patches:
            patcher.start()
            self.addCleanup(patcher.stop)

    def test_default(self):
        self.run_test(TestCaseParameters(
            args=['provision', 'vagrant'],
            expected_calls=[{
                'playbook_relative_path': 'provision/vagrant-up',
                'playbook_variables': {
                    'origin_ci_vagrant_home_dir': _default_home_dir,
                    'origin_ci_vagrant_os': OperatingSystem.fedora,
                    'origin_ci_vagrant_provider': Provider.libvirt,
                    'origin_ci_vagrant_stage': Stage.install,
                    'origin_ci_vagrant_ip': DEFAULT_MASTER_IP,
                    'origin_ci_vagrant_hostname': DEFAULT_HOSTNAME
                }
            }]
        ))

    def test_os(self):
        os = OperatingSystem.centos
        self.run_test(TestCaseParameters(
            args=['provision', 'vagrant', '--os', os],
            expected_calls=[{
                'playbook_relative_path': 'provision/vagrant-up',
                'playbook_variables': {
                    'origin_ci_vagrant_home_dir': _default_home_dir,
                    'origin_ci_vagrant_os': os,
                    'origin_ci_vagrant_provider': Provider.libvirt,
                    'origin_ci_vagrant_stage': Stage.install,
                    'origin_ci_vagrant_ip': DEFAULT_MASTER_IP,
                    'origin_ci_vagrant_hostname': DEFAULT_HOSTNAME
                }
            }]
        ))

    def test_provider(self):
        provider = Provider.virtualbox
        self.run_test(TestCaseParameters(
            args=['provision', 'vagrant', '--provider', provider],
            expected_calls=[{
                'playbook_relative_path': 'provision/vagrant-up',
                'playbook_variables': {
                    'origin_ci_vagrant_home_dir': _default_home_dir,
                    'origin_ci_vagrant_os': OperatingSystem.fedora,
                    'origin_ci_vagrant_provider': provider,
                    'origin_ci_vagrant_stage': Stage.install,
                    'origin_ci_vagrant_ip': DEFAULT_MASTER_IP,
                    'origin_ci_vagrant_hostname': DEFAULT_HOSTNAME
                }
            }]
        ))

    def test_stage(self):
        stage = Stage.base
        self.run_test(TestCaseParameters(
            args=['provision', 'vagrant', '--stage', stage],
            expected_calls=[{
                'playbook_relative_path': 'provision/vagrant-up',
                'playbook_variables': {
                    'origin_ci_vagrant_home_dir': _default_home_dir,
                    'origin_ci_vagrant_os': OperatingSystem.fedora,
                    'origin_ci_vagrant_provider': Provider.libvirt,
                    'origin_ci_vagrant_stage': stage,
                    'origin_ci_vagrant_ip': DEFAULT_MASTER_IP,
                    'origin_ci_vagrant_hostname': DEFAULT_HOSTNAME
                }
            }]
        ))

    def test_ip(self):
        ip = '127.0.0.1'
        self.run_test(TestCaseParameters(
            args=['provision', 'vagrant', '--master-ip', ip],
            expected_calls=[{
                'playbook_relative_path': 'provision/vagrant-up',
                'playbook_variables': {
                    'origin_ci_vagrant_home_dir': _default_home_dir,
                    'origin_ci_vagrant_os': OperatingSystem.fedora,
                    'origin_ci_vagrant_provider': Provider.libvirt,
                    'origin_ci_vagrant_stage': Stage.install,
                    'origin_ci_vagrant_ip': ip,
                    'origin_ci_vagrant_hostname': DEFAULT_HOSTNAME
                }
            }]
        ))

    def test_custom(self):
        os = OperatingSystem.centos
        stage = Stage.bare
        provider = Provider.vmware
        self.run_test(TestCaseParameters(
            args=['provision', 'vagrant', '--os', os, '--stage', stage, '--provider', provider],
            expected_calls=[{
                'playbook_relative_path': 'provision/vagrant-up',
                'playbook_variables': {
                    'origin_ci_vagrant_home_dir': _default_home_dir,
                    'origin_ci_vagrant_os': os,
                    'origin_ci_vagrant_provider': provider,
                    'origin_ci_vagrant_stage': stage,
                    'origin_ci_vagrant_ip': DEFAULT_MASTER_IP,
                    'origin_ci_vagrant_hostname': DEFAULT_HOSTNAME
                }
            }, {
                'playbook_relative_path': 'provision/vagrant-docker-storage',
                'playbook_variables': {
                    'origin_ci_vagrant_provider': provider,
                    'origin_ci_vagrant_home_dir': _default_home_dir,
                    'origin_ci_vagrant_hostname': DEFAULT_HOSTNAME
                }
            }]
        ))

    def test_vmware_nonbare(self):
        self.run_test(TestCaseParameters(
            args=['provision', 'vagrant', '--provider', 'vmware_fusion'],
            expected_result=CLICK_RC_USAGE,
            expected_output='Only the bare stage is supported for the vmware_fusion provider.'
        ))

    def test_destroy(self):
        patcher = patch.object(
            target=Configuration,
            attribute='registered_vagrant_machines',
            new=lambda _: [
                VagrantVMMetadata(data={
                    'directory': _default_home_dir,
                    'hostname': DEFAULT_HOSTNAME,
                    'provisioning_details': {
                        'operating_system': None,
                        'provider': None,
                        'stage': None
                    },
                    'ssh_configuration': {
                        'hostname': None,
                        'port': None,
                        'identityfile': None,
                        'user': None
                    }
                })
            ]
        )
        patcher.start()
        self.addCleanup(patcher.stop)
        self.run_test(TestCaseParameters(
            args=['provision', 'vagrant', '--destroy'],
            expected_calls=[{
                'playbook_relative_path': 'provision/vagrant-down',
                'playbook_variables': {
                    'origin_ci_vagrant_home_dir': _default_home_dir,
                    'origin_ci_vagrant_hostname': DEFAULT_HOSTNAME
                }
            }]
        ))
