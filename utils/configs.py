from utils.registry import registry
class Config():
    def __init__(self, config):
        self.config_base = config
        self.build_config()

    def build_config(self):
        self.config_base = self.config_base
        self.config_general = self.config_base["general"]
        
    def build_registry(self):
        registry.set_module("config", name="base", instance=self.config_base)
        registry.set_module("config", name="general", instance=self.config_general)
             
