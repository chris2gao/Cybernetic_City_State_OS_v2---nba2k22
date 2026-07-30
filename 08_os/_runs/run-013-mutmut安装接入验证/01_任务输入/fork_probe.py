from __future__ import annotations

import json
import os


def main() -> int:
    read_fd, write_fd = os.pipe()
    child_pid = os.fork()
    if child_pid == 0:
        os.close(read_fd)
        os.write(write_fd, b"child-ok")
        os.close(write_fd)
        os._exit(0)

    os.close(write_fd)
    child_message = os.read(read_fd, 64).decode("ascii")
    os.close(read_fd)
    waited_pid, wait_status = os.waitpid(child_pid, 0)
    result = {
        "parent_pid": os.getpid(),
        "child_pid": child_pid,
        "waited_pid": waited_pid,
        "child_message": child_message,
        "child_exit_code": os.waitstatus_to_exitcode(wait_status),
        "passed": (
            waited_pid == child_pid
            and child_message == "child-ok"
            and os.waitstatus_to_exitcode(wait_status) == 0
        ),
    }
    print(json.dumps(result, sort_keys=True))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
