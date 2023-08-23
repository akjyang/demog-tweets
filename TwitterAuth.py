import configparser


class TwitterAuth:

    def __init__(self, config_file='config.cfg'):
        self.config = configparser.ConfigParser(interpolation=None)
        self.config.read(config_file)
        self.index = None

    def set_index(self, index):
        self.index = index

    def get_index(self):
        return self.index
    
    def get_auth_profile(self, profile=None, by_index=None):
        if by_index is not None:
            index_mod = by_index % len(self.config.sections())
            index = self.config.sections()[index_mod]
            self.set_index(index)
            c = self.config[self.index]
        else:
            if profile not in self.config:
                print(f'ERROR:\t{profile} not in available auth configs. Try using  one of {self.config.sections()}:')
                raise KeyError
            c = self.config[profile]
        return dict(
            consumer_key=c["CONSUMER_KEY"],
            consumer_secret=c["CONSUMER_SECRET"], 
            access_token=c["ACCESS_TOKEN"], 
            access_token_secret=c["ACCESS_SECRET"],
            bearer_token=c["BEARER_TOKEN"]
        )
