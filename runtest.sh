#!/bin/bash
set -x

RUN_START=$(date +%s)
COREDUMP_TARGET="gnome-terminal"
TEST_REPORT_FILE="/tmp/report_$TEST.html"

# Reducing false negatives by repeating tests but not those that are expected to fail.
NON_REPEATING_TESTS=""
is_known_to_fail() {
  [[ $NON_REPEATING_TESTS =~ (^|[[:space:]])$1($|[[:space:]]) ]] && echo "0" || echo "1"
}


# Opencv setup for x86_64.
if [[ $(arch) == "x86_64" ]] && [[ ! -e /tmp/opencv_setup_done ]]; then
  python3 -m pip install opencv-python==4.5.1.48
  touch /tmp/opencv_setup_done
fi


# Setup qecore.
if [ ! -e /tmp/qecore_setup_done ]; then
  # Specify version, in case of a mistake in the next version, we still need working automation.
  python3 -m pip install qecore==3.24
  # Make the setup only once.
  touch /tmp/qecore_setup_done
fi


# In attempt to reduce false negatives, repeat tests that are not expected to fail.
MAX_FAIL_COUNT=2
for i in $(seq 1 1 $MAX_FAIL_COUNT); do

  if [[ $(arch) == "x86_64" ]]; then
    # For x86_64 respect the system setting.
    sudo -u test qecore-headless --keep-max "behave -t $1 -k -f html-pretty -o $TEST_REPORT_FILE -f plain"; rc=$?
  else
    # Fixing xorg on anything else.
    sudo -u test qecore-headless --session-type xorg --keep-max "behave -t $1 -k -f html-pretty -o $TEST_REPORT_FILE -f plain"; rc=$?
  fi

  [ $rc -eq 0 -o $rc -eq 77 ] && break
  [ "$(is_known_to_fail $1)" -eq 0 ] && break

  sleep 1
  systemctl stop gdm

done


# Mark result FAIL or PASS depending on the test result.
RESULT="FAIL"
if [ $rc -eq 0 ]; then
  RESULT="PASS"
fi


# Find out if there are any coredumps present.
coredumpctl list --since=@$RUN_START; general_dump_rc=$?

# Evaluate the coredumpctl with only relevant data being currently tested component.
coredumpctl list --since=@$RUN_START | grep $COREDUMP_TARGET; targeted_dump_rc=$?

if [ $targeted_dump_rc -eq 0 ]; then
  # Change the reported name to indicate COREDUMP in tested component has occured.
  echo "COREDUMP_${TEST}" >> /tmp/automation_debug.log

elif [ $general_dump_rc -eq 0 ]; then
  # Change the reported name to indicate that some coredump happened and INVESTIGATION could be needed.
  echo "INVESTIGATE_${TEST}" >> /tmp/automation_debug.log

fi


# Make the actual report.
rhts-report-result $TEST $RESULT $TEST_REPORT_FILE
exit $rc
