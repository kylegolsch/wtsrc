import yaml
import wtsrc.WtsrcLogger as log
from wtsrc.WtsrcSettings import CONFIG_FILE
from wtsrc.WtsrcUtils import find_file_in_tsrc_dir, find_tsrc_directory, obj_dump

class TsrcConfigModel:

    instance = None


    def __init__(self, data:dict):
        self.data = data


    def change_branch(self, branch):
        self.data['manifest_branch'] = branch

    def get_manifest_branch(self):
        return self.data.get('manifest_branch', None)

    def save(self):
        file_path = find_file_in_tsrc_dir(CONFIG_FILE)
        if file_path:
            with open(file_path, 'w') as file:
                yaml.dump(self.data, file)
        else:
            log.fatal("The tsrc config file could not be found")


    @classmethod
    def load(cls):
        if not TsrcConfigModel.instance:
            file_path = find_file_in_tsrc_dir(CONFIG_FILE)
            if file_path:
                log.perhaps_print("Attempting to load project model: {}".format(file_path))
                with open(file_path) as file:
                    yml_data = yaml.load(file, Loader=yaml.FullLoader)
                    TsrcConfigModel.instance = TsrcConfigModel(yml_data)
            else:
                log.fatal("The tsrc config file could not be found")
        return TsrcConfigModel.instance
