import sys
import socket
import contextlib
import time

class NoTracebackException(Exception):
    pass

def excepthook(exctype, value, traceback):
    if exctype == NoTracebackException:
        sys.stderr.write("ERROR: {}\n".format(str(value)))
        sys.exit(1)
    _old_excepthook(exctype, value, traceback)

def aws_vpc_by_name(ec2, vpc_name, must_exist=True):
    vpc_filter = [{"Name": "tag:Name", "Values": [vpc_name]}]
    # Here next function returns either the first item or None
    # https://docs.python.org/3/library/functions.html#next
    vpc = next(iter(ec2.vpcs.filter(Filters=vpc_filter)), None)
    if not vpc and must_exist:
        raise NoTracebackException("VPC '{}' does not exist".format(vpc_name))
    return vpc

def port_is_open(host, port):
    with contextlib.closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
        sock.settimeout(0.5)
        return sock.connect_ex((host, port)) == 0

def wait_for_ssh_port(ip, port=22):
    print("Waiting for SSH port {} to become avialable...".format(port))
    retry_count = 5
    sleep_time = 5
    for i in range(retry_count):
        if port_is_open(ip, port):
            print("Port {} is open".format(port))
            break
        else:
            print("[{}/{}] Port {} is not available. Sleeping for {} seconds".format(
                i + 1, retry_count, port, sleep_time)
            )
            time.sleep(sleep_time)

_old_excepthook = sys.excepthook
sys.excepthook = excepthook