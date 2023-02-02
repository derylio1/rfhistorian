#!/usr/bin/env python
import argparse
import os
import subprocess
import sys

import coverage
from django.core.management import execute_from_command_line


def run_tests():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rfhistorian.settings')
    os.environ.setdefault('ENVIRONMENT', 'test')
    execute_from_command_line(['manage.py', 'test', '--keepdb'])


def list_changed_in_branch():
    """Returns only files changed in current branch (compared to master)."""
    allowed_extensions = ['.html', '.py']

    res = subprocess.run(['git', 'diff', '--name-only', 'origin/master'], check=True, capture_output=True)
    return [
        file
        for file in res.stdout.decode('utf-8').split('\n')
        if any(file.endswith(ext) for ext in allowed_extensions)
    ]


def main(only_changed):
    cov = coverage.Coverage()

    if only_changed:
        cov.set_option('run:source', [])
        cov.set_option('run:include', list_changed_in_branch())

    cov.start()
    run_tests()
    cov.stop()

    cov.save()

    cov.report(file=sys.stdout)
    cov.html_report(show_contexts=True)

    try:
        os.system('open htmlcov/index.html')
    except OSError:
        print('The report is in htmlcov/index.html')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Calculate test coverage.')
    parser.add_argument('--only_changed', action='store_const', const=True, help='Only changed on current branch (compared to master)')
    args = parser.parse_args()

    main(args.only_changed)