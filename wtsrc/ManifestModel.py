import yaml
import wtsrc.WtsrcLogger as log
from wtsrc.WtsrcSettings import MANIFEST_FILE
from wtsrc.WtsrcUtils import find_file_in_manifest_dir, find_manifest_directory, obj_dump

class ManifestModel:

    instance = None

    def __init__(self, data:dict):
        self.data = data


    def log(self):
        log.print("Repos:")
        log.increase_indent()
        for r in self.data['repos']:
            for key in r:
                log.print("{k} => {v}".format(k=key, v=r[key]), color='cyan')
            log.print("")
        log.decrease_indent()


    def has_repo(self, repo_name):
        found = False
        if 'repos' in self.data:
            for repo in self.data['repos']:
                if 'dest' in repo and repo_name == repo['dest']:
                    found = True
                    break
        return found


    def update_branch(self, repo_name, branch_name):
        updated = False
        if 'repos' in self.data:
            for repo in self.data['repos']:
                if 'dest' in repo and repo_name == repo['dest']:
                    repo['branch'] = branch_name
                    updated = True
                    break

        if not updated:
            log.fatal("The repo {r} doesn't exist".format(r=repo_name))


    def save(self):
        file_path = find_file_in_manifest_dir(MANIFEST_FILE)
        if file_path:
            with open(file_path, 'w') as file:
                yaml.dump(self.data, file)
        else:
            log.fatal("The manifest file could not be found")


    @classmethod
    def load(cls):
        if not ManifestModel.instance:
            file_path = find_file_in_manifest_dir(MANIFEST_FILE)
            if file_path:
                log.perhaps_print("Attempting to load project model: {}".format(file_path))
                with open(file_path) as file:
                    yml_data = yaml.load(file, Loader=yaml.FullLoader)
                    ManifestModel.instance = ManifestModel(yml_data)
            else:
                log.fatal("The tsrc manifest file could not be found")
        return ManifestModel.instance