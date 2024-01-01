#!/usr/bin/env python3
import os
import subprocess as sp
import sys
import argparse
import datetime
import signal
from socket import gethostname
from tempfile import NamedTemporaryFile

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

def run_command_with_tee(command, log_file_path):
    with open(log_file_path, 'wb') as log_file:
        process = sp.Popen(command, stdout=sp.PIPE, stderr=sp.PIPE, text=True)

        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                print(output.strip())
                log_file.write(output.encode('utf-8'))
                log_file.flush()

        stdout, stderr = process.communicate()
        if stderr:
            print(stderr.strip())
            log_file.write(stderr.encode('utf-8'))
            log_file.flush()

    return process.returncode

def acquire_unique_filename(filename, extension):
    suffix = ''
    count = 0
    while os.path.exists(filename + suffix + extension):
        count += 1
        suffix = '-' + str(count)
    return filename + suffix + extension

def backup_filename(machine_name, part, file_system='/mnt/9', date=None):
    if not date:
        date = datetime.date.today()
    date_stamp = date.strftime('%Y%m%d')
    filename = f"{file_system}/backup/{date_stamp}-{machine_name}-{part}"
    return acquire_unique_filename(filename, '.tar.gz')

def archive_filename(name, file_system='/mnt/9', date=None):
    if not date:
        date = datetime.date.today()
    qtr = (date.month - 1) // 3 + 1
    date_stamp = date.strftime(f'%Yq{qtr}')
    filename = f"{file_system}/archive/{date_stamp}-{name}"
    return acquire_unique_filename(filename, '.tar.gz')

def lookup_part_path(part):
    part_map = {
        'root': '/',
        'home': '/home',
        'store': '/gnu/store'}
    if part in part_map:
        return part_map[part]
    else:
        return None

# Returns true on success
def execute_command(command, stdout=None, verbose=False, stderr=None):
    if stdout:
        if verbose: eprint(f'Running command: {" ".join(command)} >{stdout}')
        result = sp.run(command, check=True, stdout=stdout, stderr=stderr)
    else:
        if verbose: eprint(f'Running command: {" ".join(command)}')
        result = sp.run(command, check=True, stderr=stderr)

def execute_maybe_remote_transfer(command, machine_name, filename, stdout=None, verbose=False, remove_file=False, stderr=None):
    local = (machine_name == gethostname())
    with NamedTemporaryFile() as logfile:
        try:
            if local:
                result = execute_command(command, None, verbose, logfile)
            else:
                command = ['ssh', 'backup@'+machine_name] + command
                with open(filename, 'xb') as f:
                    result = execute_command(command, f, verbose, logfile)
            if verbose: eprint(f'Tar successfully written to ' + filename)
            return True
        except Exception as e:
            eprint(f'Caught exception: {e}')
            eprint(f'Log file saved to '+logfile.name)
            if remove_file or (os.path.isfile(filename) and os.path.getsize(filename) == 0):
                if verbose: eprint(f'Removing aborted file ' + filename)
                os.remove(filename)
            return False

def run_tar_archive(machine_name, name, path, verbose=False, exclude=[]):
    if path is None:
        eprint(f'No path is associated with part "{part}", please supply with -p.')
        return False
    local = (machine_name == gethostname())
    filename = archive_filename(name)
    assert(not os.path.exists(filename))
    parent_dir, dir_name = os.path.split(os.path.normpath(path))

    command = ['tar', '--remove-files', '-caz'] + exclude
    if verbose: command.append('-v')
    if local: command += ['-f', filename]
    else: command += ['-f', filename]
    command += ['-C', parent_dir, dir_name]
    status = execute_maybe_remote_transfer(command, machine_name, filename, verbose)
    if status == 0:
        return filename
    else:
        return None

def run_tar_backup(machine_name, part, path=None, verbose=False, extra_excludes=[]):
    if path is None:
        path = lookup_part_path(part)
        if path is None:
            eprint(f'No path is associated with part "{part}", please supply with -p.')
            return False
    else:
        path = path

    exclude = ['--one-file-system', '--exclude=/dev', '--exclude=/gnu/store', '--exclude=/sys', '--exclude=/proc', '--exclude=/mnt', '--exclude=/tmp', '--exclude=/root'] + extra_excludes
    local = (machine_name == gethostname())
    filename = backup_filename(machine_name, part)
    assert(not os.path.exists(filename))
    command = ['tar', '-caz'] + exclude
    if verbose: command.append('-v')
    if local: command += ['-f', filename]
    else: command += ['-f', '-']
    command += ['-C', '/', path]
    status = execute_maybe_remote_transfer(command, machine_name, filename, verbose)
    if status == 0:
        return filename
    else:
        return None

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='backup files to server')
    parser.add_argument('-m', '--machine', default='peter',
                        help='Name of machine to backup from, or peter for local backup')
    parser.add_argument('-v', '--verbose', action='store_true')
    parser.add_argument('-p', '--path',
                        help='Local file path')
    parser.add_argument('-x', '--exclude', nargs='*',
                        help='Additional excludes')
    parser.add_argument('-a', '--archive', action='store_true',
                        help='Remove file after it\'s been backed up, and store in archive/ directory')
    parser.add_argument('part',
                        help='The root name of the archive to create')
    # args, unknown_args = parser.parse_known_args()
    args = parser.parse_args()
    if args.verbose:
        eprint(f'verbose: {args.verbose}')
        eprint(f'part: {args.part}')
        eprint(f'path: {args.path}')
        eprint(f'machine: {args.machine}')
        eprint(f'excludes: {args.exclude}')
        eprint(f'archive: {args.archive}')
        # eprint(f'Additional args to send to tar: {unknown_args}')
    exclude = args.exclude if args.exclude is not None else []

    if args.archive:
        filename = run_tar_archive(args.machine, args.part, args.path, args.verbose, exclude)
    else:
        filename = run_tar_backup(args.machine, args.part, args.path, args.verbose, exclude)

    if filename is not None:
        print(filename)
        sys.exit(0)
    else:
        sys.exit(1)
