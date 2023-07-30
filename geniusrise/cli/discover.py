# geniusrise
# Copyright (C) 2023  geniusrise.ai
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import importlib
import inspect
import os
from abc import ABCMeta
from typing import Any

import pydantic

from geniusrise.core import Spout


class DiscoveredSpout(pydantic.BaseModel):
    name: str
    klass: type
    init_args: dict


class Discover:
    def __init__(self, directory: str):
        self.directory = directory
        self.classes: Any = {}

    def scan_directory(self):
        for root, _, files in os.walk(self.directory):
            if "__init__.py" in files:
                module = self.import_module(root)
                self.find_classes(module)
        return self.classes

    def import_module(self, path):
        path = path.replace("/", ".")
        module = importlib.import_module(path)
        return module

    def find_classes(self, module, klass=Spout):
        for name, obj in inspect.getmembers(module):
            if inspect.isclass(obj) and issubclass(obj, Spout) and obj != klass:
                self.classes[name] = DiscoveredSpout(
                    **{
                        "name": name,
                        "klass": obj,
                        "init_args": self.get_init_args(obj),
                    }
                )

    def get_init_args(self, cls):
        init_signature = inspect.signature(cls.__init__)

        init_params = init_signature.parameters
        init_args = {}
        for name, kind in init_params.items():
            if name == "self":
                continue
            if name == "kwargs" or name == "args":
                init_args["kwargs"] = Any
                continue
            if isinstance(kind.annotation, ABCMeta):
                init_args[name] = self.get_init_args(kind.annotation)
            elif kind.annotation == inspect.Parameter.empty:
                init_args[name] = "No type hint provided 😢"
            else:
                init_args[name] = kind.annotation
        return init_args
