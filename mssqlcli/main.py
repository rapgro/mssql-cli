from __future__ import unicode_literals
from __future__ import print_function

import getpass
import io
import os
import sys
from builtins import input
import click
import six
from mssqlcli.config import config_location
from mssqlcli.__init__ import __version__
from mssqlcli.mssqlclioptionsparser import create_parser

click.disable_unicode_literals_warning = True


def run_cli_with(options):

    if create_config_dir_for_first_use():
        print('created configuration directory')

    display_version_message(options)

    configure_and_update_options(options)

    # Importing MssqlCli creates a config dir by default.
    # Moved import here so we can create the config dir for first use prior.
    # pylint: disable=import-outside-toplevel
    from mssqlcli.mssql_cli import MssqlCli

    # set interactive mode to false if -Q or -i is specified
    if options.query or options.input_file:
        options.interactive_mode = False

    mssqlcli = MssqlCli(options)
    try:
        mssqlcli.connect_to_database()

        if mssqlcli.interactive_mode:
            mssqlcli.run()
        else:
            text = options.query
            if options.input_file:
                # get query text from input file
                try:
                    if six.PY2:
                        with io.open(options.input_file, 'r', encoding='utf-8') as f:
                            text = f.read()
                    else:
                        with open(options.input_file, 'r', encoding='utf-8') as f:
                            text = f.read()
                except OSError as e:
                    click.secho(str(e), err=True, fg='red')
                    sys.exit(1)
            mssqlcli.execute_query(text)
    finally:
        mssqlcli.shutdown()


def configure_and_update_options(options):
    if options.dac_connection and options.server and not \
            options.server.lower().startswith("admin:"):
        options.server = "admin:" + options.server

    if not options.integrated_auth:
        if not options.username:
            options.username = input(u'Username (press enter for sa):') or u'sa'
        if not options.password:
            pw = getpass.getpass()
            if pw is not None:
                pw = pw.replace('\r', '').replace('\n', '')
            options.password = pw


def create_config_dir_for_first_use():
    config_dir = os.path.dirname(config_location())
    if not os.path.exists(config_dir):
        os.makedirs(config_dir)
        return True

    return False


def display_version_message(options):
    if options.version:
        print('Version:', __version__)
        sys.exit(0)


def main():
    try:
        mssqlcli_options_parser = create_parser()
        mssqlcli_options = mssqlcli_options_parser.parse_args(sys.argv[1:])
        run_cli_with(mssqlcli_options)
    finally:
        print('done')


if __name__ == "__main__":
    main()
