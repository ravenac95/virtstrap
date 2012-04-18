#!/bin/sh
# file: tests/test_examples.sh
# This tests the virtstrap examples
    
. ./setup.sh

TEST_DIR=`pwd`
EXAMPLE4_DIR=$TEST_DIR/../examples/example4

oneTimeSetUp() {
    # Run virtstrap in the directory
    $VSTRAP_BIN init $EXAMPLE4_DIR
}

oneTimeTearDown() {
    # Clean up that directory
    $PYTHON_BIN cleandir.py $EXAMPLE4_DIR
}

setUp() {
    # Make sure the environment variables to test are not set
    unset DG_A
    unset DG_B
    unset DG_C
    unset DG_D
    unset DG_E

    cd $EXAMPLE4_DIR
}

tearDown() {
    cd $TEST_DIR
}

testActivateDevelopmentEnvironment() {
    . ./quickactivate

    assertSame "A" "$DG_A"
    assertSame "B" "$DG_B"
    assertSame "C" "$DG_C"
    assertSame "E" "$DG_E"

    deactivate

    assertNull "DG_A should be null" "$DG_A"
    assertNull "DG_B should be null" "$DG_B"
    assertNull "DG_C should be null" "$DG_C"
    assertNull "DG_C should be null" "$DG_E"
}

testActivateProductionEnvironment() {
    . ./quickactivate production

    assertSame "OA" "$DG_A"
    assertSame "B" "$DG_B"
    assertSame "OC" "$DG_C"
    assertSame "D" "$DG_D"
    assertNull "DG_E should be null" "$DG_E"

    deactivate

    assertNull "DG_A should be null" "$DG_A"
    assertNull "DG_B should be null" "$DG_B"
    assertNull "DG_C should be null" "$DG_C"
    assertNull "DG_D should be null" "$DG_D"
    assertNull "DG_E should be null" "$DG_E"
}

testActivateTwoEnvironments() {
    . ./quickactivate development,production

    assertSame "OA" "$DG_A"
    assertSame "B" "$DG_B"
    assertSame "OC" "$DG_C"
    assertSame "D" "$DG_D"
    assertSame "E" "$DG_E"

    deactivate

    assertNull "DG_A should be null" "$DG_A"
    assertNull "DG_B should be null" "$DG_B"
    assertNull "DG_C should be null" "$DG_C"
    assertNull "DG_D should be null" "$DG_D"
    assertNull "DG_E should be null" "$DG_E"
}

. ./shunit2
