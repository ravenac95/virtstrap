from virtstrap import commands
from virtstrap.log import logger

class CommandsCommand(commands.Command):
    name = 'commands'
    description = 'Lists commands'

    def run(self, *args, **kwargs):
        logger.info('Available Commands:')
        for command_name, command in commands.registry.commands_iter():
            logger.info('    %s: %s' % (command_name, command.description))
