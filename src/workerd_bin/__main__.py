import os
import sys

from workerd_bin import find_workerd_bin


def main() -> None:
    workerd = find_workerd_bin()
    os.execv(workerd, [workerd, *sys.argv[1:]])


if __name__ == "__main__":
    main()
