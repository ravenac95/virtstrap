"""
virtstrap_local.runner
----------------

The local project's runner.
"""
import sys
from virtstrap.runner import VirtstrapRunner
from virtstrap.loaders import *


def create_loader(args):
    main_collector = BuiltinCommandCollector('virtstrap_local.commands')
    plugin_collector = PluginCommandCollector('virtstrap_local.commands')
    return CommandLoader(collectors=[main_collector, plugin_collector])

class VirtstrapProjectLocalRunner(VirtstrapRunner):
    """Routes command line to different commands"""
    def __init__(self, *args, **kwargs):
        kwargs['loader_factory'] = create_loader
        super(VirtstrapProjectLocalRunner, self).__init__(**kwargs)

def main(args=None):
    runner = VirtstrapProjectLocalRunner()
    exit = runner.main(args=args)
    if exit:
        sys.exit(exit)
