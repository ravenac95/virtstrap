import sys
import os
import fudge
from virtstrap_local.runner import VirtstrapProjectLocalRunner

def test_runner_runs_commands_command():
    runner = VirtstrapProjectLocalRunner()
    runner.main(args=['commands'])
