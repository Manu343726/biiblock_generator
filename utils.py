import os
import urllib
import json


class CorruptSettingsError(Exception):
    pass


class GenerationSettings:
    def __init__(self, packages, variables, passwords):
        self._packages = packages
        self._variables = variables
        self._passwords = passwords

        self._check()

    def _error(self, message):
        raise CorruptSettingsError(message)

    def _check_entry(self, block, file, variable):
        blockPath = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                 "blocktemplates", block)
        filePath = os.path.join(blockPath, file)
        tag = "<" + variable + ">"

        if os.path.isdir(blockPath):
            if os.path.exists(filePath):
                with open(filePath, 'r') as f:
                    for line in f:
                        if tag in line:
                            return

                self._error("No tag '{0}' found on '{1}/{2}'".format(tag, block, file))
            else:
                self._error("No '{0}' found inside '{1}' block".format(file, block))
        else:
            self._error("No '{0}' block found in block templates directory".format(block))

    def _check(self):
        for block, (publish, replaces) in self._packages.iteritems():
            for file, variables in replaces:
                for variable in variables:
                    if variable in self._variables:
                        self._check_entry(block, file, variable)
                    else:
                        self._error("No variable corresponding to '{0}' tag found in '{1}/{2}'".format(tag, block, file))

    def packages(self):
        return self._packages

    def variables(self):
        return self._variables

    def passwords(self):
        return self._passwords


def latest_block_version(block, track):
    user = block.split("/")[0]
    url = ("https://webapi.biicode.com/v1/blocks/{0}/{1}/{2}"
           .format(user, block, track))

    try:
        data = json.loads(urllib.urlopen(url).read())
        version = str(data["version"])
    except ValueError:
        version = "-1"

    print "Found " + block + ":" + version

    return version