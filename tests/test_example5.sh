#!/bin/sh
# file: tests/test_examples.sh
# This tests the virtstrap examples
    
. ./setup.sh

TEST_DIR=`pwd`
EXAMPLE5_DIR=$TEST_DIR/../examples/example5

setUp() {
    # Make sure the environment variables to test are not set
    cd $EXAMPLE5_DIR
}

tearDown() {
    cd $TEST_DIR
}

testInitExample() {
    vstrap init
    assertEquals 0 $? 
}

. ./shunit2
