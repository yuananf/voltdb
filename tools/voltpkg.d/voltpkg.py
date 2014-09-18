# This file is part of VoltDB.
# Copyright (C) 2008-2014 VoltDB Inc.
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS BE LIABLE FOR ANY CLAIM, DAMAGES OR
# OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
# ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.

"""
Main voltpkg command module.
"""

import sys
import os
import glob
from voltcli import utility
from voltcli import environment
from lib import voltpkg_config as vpconfig
from lib import voltpkg_docker as vpdocker


class Global:
    """
    Global data.
    """
    configuration = vpconfig.ConfigurationTool('voltpkg',
        app_name=vpconfig.Property('application name', default=os.path.basename(os.getcwd())),
        base_image=vpconfig.Property('base docker image name', default='ubuntu'),
        base_tag=vpconfig.Property('base docker image tag (e.g. OS version)', default='12.04'),
        entrypoint=vpconfig.Property('docker image entrypoint (command)', default='%(dist_folder)s/bin/voltdb'),
        repo_url=vpconfig.Property('package repository URL', default='http://mirror.anl.gov/pub/ubuntu/'),
        repo_name=vpconfig.Property('package repository name', default='precise'),
        repo_sections=vpconfig.Property('package repository name', default='main restricted universe'),
        workdir=vpconfig.Property('working directory in image', default=''),
    )


@VOLT.Multi_Command(
    description  = 'Manipulate and view configuration properties.',
    modifiers = [
        VOLT.Modifier('get', Global.configuration.run_config_get,
                      'Show one or more configuration properties.',
                      arg_name = 'KEY'),
        VOLT.Modifier('reset', Global.configuration.run_config_reset,
                      'Reset configuration properties to default values.'),
        VOLT.Modifier('set', Global.configuration.run_config_set,
                      'Set one or more configuration properties (use KEY=VALUE format).',
                      arg_name = 'KEY_VALUE'),
    ]
)
def config(runner):
    runner.go()


@VOLT.Command(
    description='Create a VoltDB application Docker configuration (Dockerfile).',
    options = [
        VOLT.BooleanOption('-O', '--overwrite', 'overwrite',
                           'overwrite existing Dockerfile', default=False),
    ],
)
def docker(runner):
    config = Global.configuration.get_config(runner)
    if config is None:
        sys.exit(1)
    if os.path.exists('Dockerfile') and not runner.opts.overwrite:
        runner.abort('Dockerfile exists. Delete the file or add the -O/--overwrite option.')
    config['image_folder'] = '/opt/%(app_name)s' % config
    config['voltdb_base'] = environment.voltdb_base
    config['voltdb_bin'] = environment.voltdb_bin
    config['voltdb_lib'] = environment.voltdb_lib
    config['voltdb_voltdb'] = environment.voltdb_voltdb
    config['dockerfile_preamble'] = ('# Generated by the VoltDB "%s docker" command.'
                                            % environment.command_name)
    # Build up Dockerfile lines, expanding config symbols as we go.
    runner.info('Generating Dockerfile...')
    docker_tool = vpdocker.DockerTool(runner, config)
    docker_tool.generate()
    runner.info('Saved Dockerfile.')