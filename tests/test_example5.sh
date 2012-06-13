#!/bin/sh
# file: tests/test_example6.sh
# This tests example5
    
. ./setup.sh

TEST_DIR=`pwd`
EXAMPLE5_DIR=$TEST_DIR/../examples/example5

oneTimeSetUp() {
    true
}

oneTimeTearDown() {
    true
}

setUp() {
    # Make sure the environment variables to test are not set
    cd $EXAMPLE5_DIR
}

tearDown() {
    cd $TEST_DIR
    $PYTHON_BIN cleandir.py $EXAMPLE5_DIR
}

testInitExample5() {
    vstrap init
    assertEquals 0 $? 
}

. ./shunit2
