
from .WtsrcSettings import *
from pathlib import Path
import os
import pickle


class WtsrcModel:

    def __init__(self):
        self.aliases = {}

    def get_alias_url(self, alias_name):
        '''returns the url for the alias'''
        if alias_name in self.aliases:
            return self.aliases[alias_name]
        else:
            return None

    def add_alias(self, alias_name, url):
        '''adds an alias if it doesn't exist, throws exception if the alias already exists'''
        if alias_name in self.aliases:
            raise Exception("Alias already exists, you should delete the alias first")
        else:
            self.aliases[alias_name] = url

    def remove_alias(self, alias_name):
        '''will remove the alias if it exists'''
        self.aliases.pop(alias_name, None)

    @classmethod
    def model_file_name(cls):
        '''computes the model file name from the settings'''
        if MODEL_DIR == "$HOME":
            model_dir = Path.home()
        else:
            model_dir = MODEL_DIR

        model_file = os.path.join(model_dir, MODEL_FILE)

        return model_file

    @classmethod
    def load(cls):
        '''Returns the persisted model'''
        model_file = WtsrcModel.model_file_name()

        if(os.path.exists(model_file)):
            model = pickle.load(open(model_file, "rb"))
        else:
            model = WtsrcModel()
            model.save()

        return model

    def save(self):
        '''Saves by overwriting the model file'''
        model_file = WtsrcModel.model_file_name()
        pickle.dump(self, open(model_file, "wb" ))


    def __str__(self):
        indent = "  "
        s = "File: {}".format(WtsrcModel.model_file_name()) + "\n"
        s += "Aliases:\n"
        for alias in sorted (self.aliases.keys()):
            s += indent + "{alias} => {url}".format(alias=alias, url=self.aliases[alias])
        return s