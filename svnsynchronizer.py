from subprocess import CalledProcessError, run
from multiprocessing import Pool, freeze_support
from pathlib import Path
from typing import List
import importlib
import logging
import os
import re


PATTERN_HOST = re.compile('^(svn|https*)://(?P<host>.+?)/.*$')


def __create_logger():
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)

    formatter = logging.Formatter('[%(asctime)s][%(name)s][%(thread)d][%(levelname)s][%(message)s]')

    console_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    return logger


LOGGER = __create_logger()


def do_command(command: str, capture_output: bool = False):
    LOGGER.info(f'do command:[{command}]')
    completed = run(command, shell=True, capture_output=capture_output, text=capture_output)
    completed.check_returncode()
    return completed


def check_svn_command():
    try:
        do_command('svn --version')
    except CalledProcessError as e:
        LOGGER.exception('please check the svn command.')
        raise e


class Task:
    def __init__(self, path: str, url: str, clean: bool) -> None:
        self.path = path
        self.url = url
        self.clean = clean
        LOGGER.info(f'task path:[{self.path}] url:[{self.url}] clean:[{self.clean}]')

    def change_directory(self):
        os.chdir(self.path)
        LOGGER.info(f'current dir:[{self.path}]')

    def try_unlock(self):
        try:
            do_command('svn cleanup', capture_output=True)
        except CalledProcessError:
            pass

    def checkout_if_not(self):
        do = False
        try:
            do_command('svn info', capture_output=True)
        except CalledProcessError as e:
            do = True if 'E155007' in e.stderr else False
        LOGGER.info(f'do checkout:[{do}] path:[{self.path}] url:[{self.url}]')

        if do:
            try:
                do_command(f'svn checkout --force {self.url} .')
            except CalledProcessError as e:
                LOGGER.exception(f'svn checkout failed. path:[{self.path}] url:[{self.url}]')
                raise e

    def relocate_if_not(self):
        root_url = ''
        try:
            completed = do_command('svn info --show-item repos-root-url', capture_output=True)
            root_url = completed.stdout.replace('\n', '')
        except CalledProcessError as e:
            LOGGER.exception(f'svn info failed. path:[{self.path}] url:[{self.url}]')
            raise e

        source_match = PATTERN_HOST.match(root_url)
        if not source_match:
            LOGGER.critical(f'host parsing failed. root url:[{root_url}]')
            raise Exception()
        source_host = source_match.group('host')

        dest_match = PATTERN_HOST.match(self.url)
        if not dest_match:
            LOGGER.critical(f'host parsing failed. root url:[{self.url}]')
            raise Exception()
        dest_host = dest_match.group('host')

        do = source_host != dest_host
        LOGGER.info(f'do relocate:[{do}] path:[{self.path}] url:[{self.url}]')

        if do:
            do_command(f'svn relocate {self.url}')

    def switch_if_not(self):
        url = ''
        try:
            completed = do_command('svn info --show-item url', capture_output=True)
            url = completed.stdout.replace('\n', '')
        except CalledProcessError as e:
            LOGGER.exception(f'svn info failed. path:[{self.path}] url:[{self.url}]')
            raise e
        do = self.url != url
        LOGGER.info(f'do switch:[{do}] path:[{self.path}] url:[{self.url}]')

        if do:
            do_command(f'svn switch {self.url}')

    def cleanup_if(self):
        if self.clean:
            do_command('svn cleanup --remove-unversioned --remove-ignored')
            do_command('svn revert --recursive --remove-added .')

    def update(self):
        do_command('svn update')


def do(task: Task):
    task.change_directory()
    task.try_unlock()
    task.checkout_if_not()
    task.relocate_if_not()
    task.switch_if_not()
    task.cleanup_if()
    task.update()


if __name__ == '__main__':
    freeze_support()
    check_svn_command()

    config = importlib.import_module('config')

    tasks: List[Task] = []
    for repo in config.REPOSITORIES:
        path = str(Path(os.path.expanduser(os.path.expandvars(repo['path']))))
        os.makedirs(path, exist_ok=True)
        tasks.append(Task(path, repo['url'], repo['clean']))

    with Pool(os.cpu_count()) as p:
        p.map(do, tasks)
