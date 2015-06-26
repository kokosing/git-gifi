import argparse


def main():
    parser = argparse.ArgumentParser(description='Git and github enhancements to git.')
    parser.add_argument('command', metavar='command', type=str, nargs=1,
                                        help='comand to run')

    args = parser.parse_args()
    print args.command
