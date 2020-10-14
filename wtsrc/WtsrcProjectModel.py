import yaml
import wtsrc.WtsrcLogger as log
from wtsrc.WtsrcSettings import WTSRC_FILE
from wtsrc.WtsrcUtils import find_file_in_manifest_dir, find_manifest_directory, obj_dump

def get_from_dict(dict, field, field_description, is_required, type=None):

    if field in dict:
        data = dict[field]
        if type and not isinstance(data, type):
            log.fatal("{0} is was not the expected type".format(field_description))
    elif is_required:
        log.fatal(log.fatal("{0} is required, but not found".format(field_description)))
    else:
        data = None

    return data


class WtsrcProjectModel:

    class Action:
        def __init__(self, name, action, comment):
            self.name = name
            self.action = action
            self.comment = comment


        @classmethod
        def create_from_dict(cls, name:str, data:dict):
            action = get_from_dict(data, 'action', 'action field for {}'.format(name), True, str)
            comment = get_from_dict(data, 'comment', 'comment field for {}'.format(name), False, str)
            return WtsrcProjectModel.Action(name, action, comment)


        def log(self):
            log.print("name: {}".format(self.name), color='cyan')
            log.increase_indent(" -")
            log.print("comment: {}".format(self.comment))
            log.print("action:  {}".format(self.action))
            log.decrease_indent()


    class Command:
        def __init__(self, name, pre_action, post_action):
            self.name = name
            self.pre_action = pre_action
            self.post_action = post_action


        @classmethod
        def create_from_dict(cls, name:str, data:dict):
            pre = get_from_dict(data, 'pre', 'pre field for command {}'.format(name), False, str)
            post = get_from_dict(data, 'post', 'pre field for command {}'.format(name), False, str)
            return WtsrcProjectModel.Command(name, pre, post)


        def log(self):
            log.print("name: {}".format(self.name), color='cyan')
            log.increase_indent(" -")
            log.print("pre:  {}".format(self.pre_action))
            log.print("post: {}".format(self.post_action))
            log.decrease_indent()


    # singleton
    instance = None
    known_commands = None
    pre_action_not_possible_cmds = {}
    post_action_not_possible_cmds = {}

    def __init__(self, data:dict):
        self.commands = {}
        self.actions = {}

        # parse the 'commands' section of the dictionary
        if 'commands' in data:
            self.process_commands_dict(data['commands'])
        else:
            log.warning("'commands' section not found in {} file".format(WTSRC_FILE))

        # parse the 'actions' section of the dictionary
        if 'actions' in data:
            self.process_actions_dict(data['actions'])
        else:
            log.warning("'actions' section not found in {} file".format(WTSRC_FILE))


    def process_actions_dict(self, actions:dict):
        if isinstance(actions, dict):
            for action_name in actions:
                self.add_action(action_name, actions[action_name])
        else:
            log.fatal("{} - 'actions' is not a dictionary".format(WTSRC_FILE))


    def add_action(self, name:str, action:dict):
        if name in self.actions:
            log.fatal("'{a}' action is defined in {f} more than once".format(a=name, f=WTSRC_FILE))

        self.actions[name] = WtsrcProjectModel.Action.create_from_dict(name, action)

    def process_commands_dict(self, commands:dict):
        if isinstance(commands, dict):
            for cmd_name in commands:
                self.add_command(cmd_name, commands[cmd_name])
        else:
            log.fatal("{} - 'commands' is not a dictionary".format(WTSRC_FILE))


    def add_command(self, name:str, cmd:dict):
        if name in self.commands:
            log.fatal("'{c}' command is defined in {f} more than once".format(c=name, f=WTSRC_FILE))

        if WtsrcProjectModel.known_commands and not name in WtsrcProjectModel.known_commands:
            log.warning("{f} defines actions for command '{c}' that is not a wtsrc command".format(f=WTSRC_FILE, c=name))

        self.commands[name] = WtsrcProjectModel.Command.create_from_dict(name, cmd)

        if name in WtsrcProjectModel.pre_action_not_possible_cmds and self.commands[name].pre_action:
            log.warning("{f} defines a pre-action for command '{c}' that cannot be executed by wtsrc".format(f=WTSRC_FILE, c=name))

        if name in WtsrcProjectModel.post_action_not_possible_cmds and self.commands[name].post_action:
            log.warning("{f} defines a post-action for command '{c}' that cannot be executed by wtsrc".format(f=WTSRC_FILE, c=name))


    def get_command_pre_action(self, cmd_name:str):
            cmd = self.commands.get(cmd_name, None)
            if cmd:
                cmd = cmd.pre_action
            return cmd


    def get_command_post_action(self, cmd_name:str):
            cmd = self.commands.get(cmd_name, None)
            if cmd:
                cmd = cmd.post_action
            return cmd


    def get_action_action(self, action_name:str):
            action = self.actions.get(action_name, None)
            if action:
                action = action.action
            return action


    @staticmethod
    def register_known_command(cmd_name):
        '''Tells the model that there is a command with the specified name'''
        if not WtsrcProjectModel.known_commands:
            WtsrcProjectModel.known_commands = {}
        # the following line has a warning because known_commands was initially set to None - to avoid adding a flag when no commands are registered
        WtsrcProjectModel.known_commands[cmd_name] = True


    @staticmethod
    def register_pre_action_not_possible_cmd(cmd_name):
        '''Tells the model that it isn't possible to run the pre-command action on this command'''
        WtsrcProjectModel.pre_action_not_possible_cmds[cmd_name] = True


    @staticmethod
    def register_post_action_not_possible_cmd(cmd_name):
        '''Tells the model that it isn't possible to run the post-command action on this command'''
        WtsrcProjectModel.post_action_not_possible_cmds[cmd_name] = True


    @classmethod
    def load(cls):
        if not WtsrcProjectModel.instance:
            file_path = find_file_in_manifest_dir(WTSRC_FILE)

            if file_path:
                log.perhaps_print("Attempting to load project model: {}".format(file_path))
                with open(file_path) as file:
                    yml_data = yaml.load(file, Loader=yaml.FullLoader)
                    WtsrcProjectModel.instance = WtsrcProjectModel(yml_data)
            else:
                manifest_dir = find_manifest_directory()
                log.warning("The wtsrc project file could not be found at: {}".format(manifest_dir))
                if not manifest_dir:
                    log.warning("You probably are not calling from within a tsrc project directory")
                WtsrcProjectModel.instance = WtsrcProjectModel({'commands': {}, 'actions': {}})

        return WtsrcProjectModel.instance


    def log(self):
        log.print("Commands:")
        log.increase_indent("  ")
        for cmd_name in self.commands:
            self.commands[cmd_name].log()
            log.print("", indent=False)
        log.decrease_indent()

        log.print("Actions:")
        log.increase_indent("  ")
        for action_name in self.actions:
            self.actions[action_name].log()
            log.print("", indent=False)
        log.decrease_indent()
