"""
VirtstrapConfig
===============

VirtstrapConfig is an interface to the VEfile. It collects the VEfile's 
settings between all the applicable profiles. It provides a way to query
for a compiled section of data within the VirtstrapConfig.
"""
try:
    # First try to use PyYAML
    import yaml
except ImportError:
    # Fallback to simpleyaml if PyYAML isn't found
    import simpleyaml as yaml

class ConfigurationError(Exception):
    pass

class ConfigurationCompilationError(Exception):
    pass

class VirtstrapConfig(object):
    @classmethod
    def from_string(cls, string, profiles=None):
        config = cls(profiles=profiles)
        config.parse(string)
        return config

    @classmethod
    def from_file(cls, filename, profiles=None):
        try:
            string = open(filename)
        except IOError:
            string = ''
        return cls.from_string(string, profiles=profiles)

    def __init__(self, profiles=None):
        # The default profile is ALWAYS processed no exceptions
        self._profiles = ['default']
        # Done here and there
        self._profiles.extend(profiles or [])
        self._processed_sections = {}

    def parse(self, string):
        raw_config_data = yaml.load_all(string)
        profile_data = {}
        for profile in raw_config_data:
            profile_name = profile.get('profile', 'default')
            if profile_name in profile_data:
                raise ConfigurationError('Profile "%s" found again. Cannot '
                        'have the same profile multiple times' % profile_name)
            profile_data[profile_name] = profile
        self._raw_profile_data = profile_data

    def set_profiles(self, profiles):
        """Sets the profiles. It also resets the processed settings"""
        self._profiles = ['default']
        self._profiles.extend(profiles)
        self._processed_sections = {}

    def get_profile(self):
        return self._profiles

    def section(self, section_name):
        raw_profile_data = self._raw_profile_data
        # process all of the profiles requested
        compiled_data = None
        for profile in self._profiles:
            profile_data = raw_profile_data.get(profile, {})
            section_data = profile_data.get(section_name, None)
            if section_data:
                if compiled_data and type(compiled_data) != type(section_data):
                    raise ConfigurationCompilationError('Sections contain '
                            'incompatible data. '
                            'You cannot mix a list and a dict')
                if isinstance(compiled_data, dict):
                    compiled_data.update(section_data)
                elif isinstance(compiled_data, list):
                    compiled_data.extend(section_data)
                else:
                    if isinstance(section_data, dict):
                        compiled_data = section_data.copy()
                    elif isinstance(section_data, list):
                        compiled_data = section_data[:]
                    else:
                        compiled_data = section_data
        return compiled_data

    def process_section(self, section_name, process_function):
        raw_section = self.section(section_name)
        processed_section = process_function(raw_section)
        self._processed_sections[section_name] = processed_section
        return processed_section

    def processed_section(self, section_name):
        """Get's the processed data for a section name"""
        return self._processed_sections.get(section_name)
