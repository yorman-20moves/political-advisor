# my_agent/utils/custom_logging.py

import logging
from typing import Dict

class StateLogHandler(logging.Handler):
    def __init__(self, state: Dict):
        super().__init__()
        self.state = state

    def emit(self, record):
        log_entry = self.format(record)
        if 'log_messages' not in self.state:
            self.state['log_messages'] = []
        self.state['log_messages'].append(log_entry)