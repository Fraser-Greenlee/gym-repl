import string
import numpy as np
from gym import Env
from gym.spaces import Discrete, Box
from six import StringIO
import sys

CHARS = string.digits + '-E '
OUTPUT_LEN = 10
EMPTY_STATE = ' ' * OUTPUT_LEN


class ReplEnv(Env):
    action_space = Discrete(4)  # write 1, write +, write -, run
    act_code_map = ['1', '+', '-', 'clear']
    current_code = ''

    observation_space = Box(0, len(CHARS)-1, shape=(OUTPUT_LEN, 1), dtype=int)
    state = EMPTY_STATE

    def __init__(self):
        self.metadata = {'render.modes': ['human', 'ansi']}

    @staticmethod
    def _format_output(out):
        no_newline = out[:-1]
        if len(out) > OUTPUT_LEN:
            return no_newline[:OUTPUT_LEN + 1]
        return no_newline + ' ' * (OUTPUT_LEN - len(no_newline))

    def _run_code(self, code):
        old = sys.stdout
        stdout = StringIO()
        sys.stdout = stdout
        try:
            exec('print({0})'.format(code))
            out = stdout.getvalue()
        except SyntaxError:
            out = 'E\n'
        sys.stdout = old
        return self._format_output(out)

    @property
    def encoded_state(self):
        one_hot = np.zeros((OUTPUT_LEN, len(CHARS)))
        one_hot[np.arange(OUTPUT_LEN), [CHARS.index(c) for c in self.state]] = 1
        return one_hot.reshape(-1)

    def step(self, action):
        code_token = self.act_code_map[action]
        if code_token == 'clear':
            self.current_code = ''
        elif len(self.current_code) >= OUTPUT_LEN:
            self.current_code = ''
        else:
            self.current_code += code_token
        self.state = self._run_code(self.current_code)
        reward = 0
        info = {}
        done = False
        return self.encoded_state, reward, done, info

    def render(self, mode='human', close=False):
        if mode not in self.metadata['render.modes']:
            raise RuntimeError('Render mode %s not a valid.' % mode)
        if close:
            return

        outfile = StringIO() if mode == "ansi" else sys.stdout
        outfile.write('>>> {}\n{}\n'.format(self.current_code, self.state))
        return outfile

    def reset(self):
        self.current_code = ''
        self.state = EMPTY_STATE
        return self.encoded_state
