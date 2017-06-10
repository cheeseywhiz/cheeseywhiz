"""\
Provides html file visualization of a json dataset
"""
import json
import subprocess


class JsonVis:
    def _open_list(self):
        self.instructions.append(('open_list', None))

    def _list_item(self, data):
        self.instructions.append(('list_item', str(data)))

    def _close_list(self):
        self.instructions.append(('close_list', None))

    def _iterate(self, data: iter):
        if isinstance(data, dict):
            for key, value in data.items():
                self._iterate(key)
                self._open_list()
                self._iterate(value)
                self._close_list()
        elif isinstance(data, list):
            self._open_list()
            for item in data:
                self._iterate(item)
            self._close_list()
        else:
            self._list_item(data)

    def download(self, url: str):
        """
        Return a python dictionary generated from json data at <url>.
        """
        data = subprocess.run(
            f"curl '{url}'",  # Quotes required around url for URL parameters
            stdout=subprocess.PIPE,
            shell=True
        ).stdout
        self.data = json.loads(data)
        return self

    def make_instructions(self):
        """
        Return a list of instructions that is parsed by the json.html template.
        """
        self.instructions = []
        self._open_list()
        self._iterate(self.data)
        self._close_list()
        return self.instructions
