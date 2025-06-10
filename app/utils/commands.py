import subprocess


def run_command_as_user(username, command):
    subprocess.run(['sudo', '-u', username] + command, check=True)
