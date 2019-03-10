import sys

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

_old_excepthook = sys.excepthook
sys.excepthook = excepthook