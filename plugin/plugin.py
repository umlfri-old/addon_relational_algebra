#!/usr/bin/python
from DRA import *
import sys
import os


def pluginMain(interface):
    dra=DRA(interface)
    dra.pluginMain()
