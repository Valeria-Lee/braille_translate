#!/usr/bin/env bash

set -e

apt-get install -y portaudio19-dev python3-pyaudio
pip install -r requirements.txt