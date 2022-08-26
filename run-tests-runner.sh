#!/bin/bash
# -*- coding: utf-8 -*-

sleep 10
ls -la
python3 -m pytest -rx /eudat/b2share/tests -W ignore::DeprecationWarning > /proc/1/fd/1 2>&1