#!/usr/bin/env python
# -*- coding: utf-8 -*-
import click
import os
import pprint
import subprocess
import sys
from yaml import load, YAMLError

import travis_helpers


def _load_travis_conf(mqt_path):

    with open(os.path.join(mqt_path, '.travis.yml'), 'r') as stream:
        try:
            travis = load(stream)
        except YAMLError as exc:
            print(exc)

    pprint.pprint(travis)

    return travis


class SH(object):

    def __init__(self, mqt_path, env=None):
        self.mqt_path = mqt_path
        self.env = env

    def exe(self, command, exit_on_error=True):

        if isinstance(command, (str, unicode)):
            pass
        elif isinstance(command, list):
            command = ' '.join(command)
        else:
            raise Exception(
                "Command should be a str, unicode or a list, found %s (%s)" % (
                    type(command), command))

        command = command.replace('${TRAVIS_BUILD_DIR}', self.mqt_path)

        if self.env:
            command = "%s %s" % (self.env, command)

        print(travis_helpers.green("Exec: %s" % command))
        exit_code = subprocess.call(command, shell=True)

        if exit_code > 0:
            msg = 'ERROR while execulting: %s' % command
            print(travis_helpers.red(msg))
            if exit_on_error:
                sys.exit(msg)
        return exit_code

    def update_env(self, new_envs):
        self.env = '%s %s' % (self.env, new_envs)


def execute_script(sh, job_id, script_exec, script_filter):
    if script_filter and script_filter not in script_exec:
        print(travis_helpers.dark_grey(
            "Command argument script set, only script %s to execute" %
            script_filter))
        return
    res = sh.exe(script_exec, exit_on_error=False)
    if res > 0:
        print(travis_helpers.red("Error in job %s, script: %s" % (
            job_id, script_exec)))
        print (
            "Execute only that failed test with command: "
            "./run.py -j %s -s %s" % (job_id, script_filter))
        sys.exit(1)


@click.command()
@click.argument(
    'mqt-path',
    default='/opt/openerp/code/github-trobz/maintainer-quality-tools')
@click.option('--job', '-j', type=int)
@click.option('--script', '-s')
def run(mqt_path, job, script):
    '''
    Run equivalent of travis tests
    '''

    travis = _load_travis_conf(mqt_path)

    sh = SH(mqt_path, 'TRAVIS_BUILD_DIR="%s"' % (mqt_path))
    sh.update_env('TRAVIS_BRANCH="HEAD"')
    sh.update_env(travis['env']['global'][0])

    sh.exe('rm -rf $HOME/maintainer-quality-tools')

    os.chdir(mqt_path)

    for install in travis['install']:
        if install.startswith('export '):
            sh.env += install[6:]
            continue
        if 'travis_install_nightly' in install:
            print(
                'Skipped because requires sudo and anyway, '
                'only need to do once. You have to do it manually.')
            continue

        sh.exe(install)

    job_id = 1
    global_env = sh.env
    print(global_env)
    env_jobs = travis['env']['matrix']
    for job_env in env_jobs:
        if job and job != job_id:
            print("Command argument job set, only job %s to execulte. "
                  "Skipping job env %s" % (job, job_id))
            job_id += 1
            continue

        sh.env = global_env
        print("----------------------------------------------------------")
        print("Job %s: %s" % (job_id, job))
        print("----------------------------------------------------------")

        if not ('TESTS="0"' in job_env and 'LINT_CHECK="1"' in job_env):
            print(travis_helpers.dark_grey(
                'Skipping, only LINT_CHECK supported for now'))
            job_id += 1
            continue
        sh.update_env(job_env)

        execute_script(sh, job_id, 'travis_run_tests 8.0', script)
        execute_script(sh, job_id, 'self_tests', script)

        job_id += 1

if __name__ == '__main__':
    run()
