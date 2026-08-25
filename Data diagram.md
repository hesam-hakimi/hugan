TASK: VERIFY_LOCAL_PROCESS_EXECUTION_FOR_REPAIR_11

This is a preflight-only check.

Do not inspect or modify source files.
Do not modify the repository.
Do not build, package, install, or start Runtime QA.

Run these exact executables directly:

1. C:\Windows\System32\cmd.exe /c echo PROCESS_EXECUTION_OK
2. C:\Program Files\TD Git\cmd\git.exe –version
3. C:\Program Files\nodejs\node.exe –version
4. C:\Program Files\nodejs\npm.cmd –version

For each command report:

* resolved executable path;
* visible output;
* exit code.

PASS requires:

* all four processes launch;
* all four return visible output;
* all four return exit code 0;
* the first output contains PROCESS_EXECUTION_OK.

If PASS, return:

PROCESS_EXECUTION_AVAILABLE: YES
READY_TO_RUN_REPAIR_11: YES
LOCAL_PROCESS_GATE_RESULT: PASS

Otherwise return:

PROCESS_EXECUTION_AVAILABLE: NO
READY_TO_RUN_REPAIR_11: NO
LOCAL_PROCESS_GATE_RESULT: BLOCKED
