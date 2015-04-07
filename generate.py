import settings # note there should be a settings.py module in the path or working directory
import subprocess
import os
import argparse


class generator(object):

    def default_cli(self):
        cli_parser = argparse.ArgumentParser()

        cli_parser.add_argument("track", help="biicode track that will be generated")

        cli_parser.add_argument("--ci-build", "-ci", help="Specifies if the generation is being run inside a CI build",
                            action="store_true", dest="ci")
        cli_parser.add_argument("--passwords", "-pass",
                            help=("Dictionary containing block accounts passwords to be able to publish. "
                                  "Note that with publish disabled the passwords are not needed"),
                            default="{}")
        cli_parser.add_argument("--no-publish", "-nopublish", help="Overrides publish settings and does not publish any block",
                            action="store_true", dest="no_publish")
        cli_parser.add_argument("--publish-examples", help="Enables block examples publication",
                            action="store_true", dest="publish_examples")
        cli_parser.add_argument("--tag", help="biicode version tag which blocks will be published",
                            default="DEV")
        cli_parser.add_argument("--exclude", help="Exclude explicitly blocks from generation. Pass block names separated with spaces",
                            default="")

        return cli_parser

    def __init__(self):
        __settings = settings.settings(self.default_cli())
        self.packages = __settings.packages()
        self.variables = __settings.variables()
        self.passwords = __settings.passwords()
        self.projectDir = os.path.dirname(os.path.abspath(__file__))

        self.blocks_directory = os.path.join(os.path.dirname(os.path.abspath(__file__)), "blocks")
        self.templates_directory = os.path.join(os.path.dirname(os.path.abspath(__file__)), "blocktemplates")

    def setting_to_tag(self, setting):
        """Returns the file template tag corresponding to a specific setting"""

        return "<{0}>".format(setting.upper())

    def replace(self, template, block, track, file):
        """Replaces the tags on the file template with the settings"""

        for variable, value in self.variables.iteritems():
            if self.setting_to_tag(variable) in template:
                template = template.replace(self.setting_to_tag(variable),
                                            value(block, track, file))

        return template

    def working_track(self):
        return self.variables["WORKING_TRACK"](None, None, None)

    def execute(self):
        from shutil import copytree, rmtree, ignore_patterns

        for block, (publish_block, entry) in sorted(self.packages.iteritems()):
            print "Processing " + block
            print "="*30

            template_files = [x[0] for x in entry]

            #Copy block contents except templates to blocks/block

            rmtree(os.path.join(self.blocks_directory, block), ignore_errors=True)
            copytree(os.path.join(self.templates_directory, block),
                     os.path.join(self.blocks_directory, block),
                     ignore_patterns(template_files))

            for template, _ in entry:
                print " - " + template

                ifile = open(os.path.join(self.templates_directory, block, template), 'r')
                ofile = open(os.path.join(self.blocks_directory, block, template), 'w')

                ofile.write(self.replace(ifile.read(),
                                         block,
                                         self.working_track(),
                                         template))

                ifile.close()
                ofile.close()

            if publish_block != "disabled":
                print "Publishing '{0}({1})'".format(block, self.working_track())

                user = block.split('/')[0]

                login = subprocess.Popen(['bii', 'user', '-p', self.passwords[user], user], cwd=self.projectDir)
                login.wait()

                out, _ = subprocess.Popen(['bii', 'user'], cwd=self.projectDir, stdout=subprocess.PIPE).communicate()
                if not user in out:
                    raise RuntimeError("Failed logging in as '" + user + "'. bii user output: \"" + out + "\"")

                publish = subprocess.Popen(['bii', 'publish', block, '--tag', publish_block], cwd=self.projectDir)
                publish.wait()


def run():
    #Ok Diego, here's your login
    login = subprocess.Popen(['bii', 'user', "palmeritaman"], cwd=os.path.dirname(os.path.abspath(__file__)))
    login.wait()

    generator().execute()

if __name__ == '__main__':
    run()
