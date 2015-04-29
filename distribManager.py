#!/usr/bin/python3
#
# Ariane community distrib main
#
# Copyright (C) 2014 Mathilde Ffrench
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
from tools.Parser import Parser
import os

__author__ = 'mffrench'


if __name__ == "__main__":

    args = Parser("community").parse()
    
    # Get full path of script and remove script name
    path = '/'.join(os.path.realpath(__file__).split('/')[:-1])

    try:
        dir(args).index("func")
    except ValueError as e:
        print("To get Ariane Distribution Manager help add -h or --help option to command line")
        exit(0)

    try:
        args.func(args,path)
    except ValueError as e:
        print("{0}".format(e))
    except RuntimeError as e:
        print("{0}".format(e))
