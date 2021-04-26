#!/usr/bin/env python
# -*- coding:utf-8 -*-
import os
import json
import shutil
from tempfile import NamedTemporaryFile

from ansible.cli import CLI
from ansible.executor.playbook_executor import PlaybookExecutor
from ansible.module_utils.common.collections import ImmutableDict
from ansible.parsing.dataloader import DataLoader
from ansible.inventory.manager import InventoryManager
from ansible.plugins.callback import CallbackBase
from ansible.vars.manager import VariableManager
from ansible import constants
from ansible import context

class AnsibleTaskExecutor(object):
    def __init__(self):
        self.loader = DataLoader()
        constants.HOST_KEY_CHECKING = False

    def execute(self, playbook_source, hosts_source, extra_vars=None, tags=[]):
        context.CLIARGS = ImmutableDict(tags=tags, listtags=False, listtasks=False, listhosts=False, syntax=False,
                                        connection='ssh', module_path=None, forks=100, remote_user='root',
                                        private_key_file=None, ssh_common_args=None, ssh_extra_args=None,
                                        sftp_extra_args=None, scp_extra_args=None, become=False, become_method='sudo',
                                        become_user='root', verbosity=True, check=False, start_at_task=None,
                                        )
        with NamedTemporaryFile(mode='w') as hosts_file:
            hosts_file.write(hosts_source)
            hosts_file.seek(0)
            inventory = InventoryManager(loader=self.loader, sources=(hosts_file.name,))

        variable_manager = VariableManager(loader=self.loader, inventory=inventory,
                                           version_info=CLI.version_info(gitinfo=False))
        if extra_vars:
            variable_manager._extra_vars = extra_vars

        playbook = os.path.abspath("playbooks/" + playbook_source)
        pbex = PlaybookExecutor(playbooks=[playbook], inventory=inventory,
                                variable_manager=variable_manager, loader=self.loader, passwords={})
        result_callback = ResultCallback()
        pbex._tqm._stdout_callback = result_callback
        result_code = pbex.run()

        # Remove ansible tmpdir
        shutil.rmtree(constants.DEFAULT_LOCAL_TMP, True)

        return result_code, result_callback


class ResultCallback(CallbackBase):
    def __init__(self, *args, **kwargs):
        super(ResultCallback, self).__init__(*args, **kwargs)
        self.host_ok = []
        self.host_unreachable = []
        self.host_failed = []

    def v2_runner_on_unreachable(self, result, ignore_errors=False):
        self.host_unreachable.append(dict(host=result._host.get_name(), task=result._task.get_name(),
                                          result=result._result))

    def v2_runner_on_ok(self, result, *args, **kwargs):
        self.host_ok.append(dict(host=result._host.get_name(), task=result._task.get_name(),
                                 result=result._result))

    def v2_runner_on_failed(self, result, *args, **kwargs):
        self.host_failed.append(dict(host=result._host.get_name(), task=result._task.get_name(),
                                     result=result._result))

    def get_all_result(self):
        return json.dumps(dict(ok=self.host_ok, unreachable=self.host_unreachable, failed=self.host_failed), indent=3)
