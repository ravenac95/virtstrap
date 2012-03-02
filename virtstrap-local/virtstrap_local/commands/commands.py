import json
from argparse import ArgumentParser
from virtstrap import commands
from virtstrap.log import logger

parser = ArgumentParser()
parser.add_argument('--as-json', action='store_true',
        dest='as_json')

class CommandsCommand(commands.Command):
    name = 'commands'
    description = 'Lists commands (Excludes self from commands)'
    parser = parser

    def run(self, options, **kwargs):
        collected_commands = self.collect_commands()
        if options.as_json:
            self.display_json(collected_commands)
        else:
            self.display_readable(collected_commands)

    def collect_commands(self):
        collected = []
        for command_name, command in commands.registry.commands_iter():
            if command_name == self.name:
                continue
            collected.append(dict(name=command.name, 
                description=command.description))
        return collected

    def display_json(self, collected_commands):
        json_string = json.dumps(dict(commands=collected_commands))
        logger.info(json_string)
            
    def display_readable(self, collected_commands):
        logger.info('Available Commands:')
        for command in collected_commands:
            logger.info('    %s: %s' % 
                    (command['name'], command['description']))
