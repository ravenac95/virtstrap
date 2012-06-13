#!/bin/sh
# file: tests/test_example6.sh
# This tests the virtstrap examples
    
. ./setup.sh

TEST_DIR=`pwd`
EXAMPLE6_DIR=$TEST_DIR/../examples/example6
EXAMPLE6_PROJ_DIR=$EXAMPLE6_DIR/project
EXAMPLE6_ENV_DIR=$EXAMPLE6_DIR/env

oneTimeSetUp() {
    true
}

oneTimeTearDown() {
    true
}

setUp() {
    # Make sure the environment variables to test are not set
    cd $EXAMPLE6_PROJ_DIR
}

tearDown() {
    cd $TEST_DIR
    $PYTHON_BIN cleandir.py $EXAMPLE6_PROJ_DIR
    rm -r $EXAMPLE6_ENV_DIR
}

testInitExample6() {
    vstrap init --virtstrap-dir=../env
    rm .vs.env
    . ./quickactivate # The ./ is required for ksh
    assertEquals "WORLD" "$HELLO"
}

. ./shunit2
