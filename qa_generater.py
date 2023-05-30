# -*- coding: utf-8 -*-

import openai
import time
import datetime
import logging
import multiprocessing
import pandas as pd

from openai_apikey import api_key

openai.api_key = api_key


class QAGenerater:
    def __init__(self) -> None:
        pass