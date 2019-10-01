import numpy as np
from gym import Env
from gym.spaces import Discrete, Box
from six import StringIO
import sys
import string
all_input_output_chars = string.printable[:-3]

CHAR_COUNT = len(all_input_output_chars)
MAX_INPUT_LEN = 30
MAX_OUTPUT_LEN = 30


class ReplEnv(Env):
    action_space = Box(0, len(CHAR_COUNT) - 1, shape=(MAX_INPUT_LEN, 1), dtype=int)
    current_code = ''
    observation_space = Box(0, len(CHAR_COUNT) - 1, shape=(MAX_OUTPUT_LEN, 1), dtype=int)
    state = ''

    def __init__(self):
        self.metadata = {'render.modes': ['human', 'ansi']}

    def _run_code(self, code):
        old = sys.stdout
        stdout = StringIO()
        sys.stdout = stdout
        try:
            exec('print({0})'.format(code))
            out = stdout.getvalue()
        except Exception:
            out = 'E\n'
        sys.stdout = old
        return out[:-1][:MAX_OUTPUT_LEN]

    def step(self, code):
        if len(self.current_code) >= MAX_OUTPUT_LEN:
            self.current_code = ''
        else:
            self.current_code = code
        self.state = self._run_code(self.current_code)
        reward = 0
        info = {}
        done = False
        return self.state, reward, done, info

    def render(self, mode='human', close=False):
        if mode not in self.metadata['render.modes']:
            raise RuntimeError('Render mode %s not a valid.' % mode)
        if close:
            return
        outfile = StringIO() if mode == "ansi" else sys.stdout
        code_str = ''.join(['>>> {}\n'.format(code) for code in self.current_code.split('\n')])
        outfile.write('{}{}\n'.format(code_str, self.state))
        return outfile

    def reset(self):
        self.current_code = ''
        self.state = ''
        return self.state
