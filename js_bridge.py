import os

class js_bridge():
    """
    This class creates and executes very simple JavaScript code files in order to deploy, operate and communicate with
    contracts created by cov_gen.
    The files this class creates look like this:

import { BITBOX } from 'bitbox-sdk';
import { Contract, SignatureTemplate } from 'cashscript';
...
((global_scope_code))
...
async function main() {
    ...
    ((main_scope_code))
    ...
}
main();


    """

    def __init__(self, file_path: str = '_temp.js'):

        self.f = file_path

        self.g_lines = []   # global scope code
        self.m_lines = []   # main scope code


    def new(self, file_path: str = '_temp.js'):
        self.f = file_path
        self.lines = []

    def print(self, s):
        self.lines.append('console.log({});'.format(s))

    def get_script(self):
        """
        We assume a very simple js file with a single function which is called main
        :return: string
        """

        full_script = []

        full_script.append("import { BITBOX } from 'bitbox-sdk';")
        full_script.append("import { Contract, SignatureTemplate } from 'cashscript';")
        full_script = full_script + self.g_lines
        full_script.append("async function main() {")
        full_script = full_script + ['\t' + l for l in self.m_lines]
        full_script.append("}")
        full_script.append("main();")

        return '\n'.join(full_script)

    def save(self):
        with open(self.f, "w") as f:
            print(self.get_script(), file=f)

    def run(self):
        os.system("node " + self.f)

