from gym import Env
from gym.spaces import Discrete, Box
import numpy as np
from six import StringIO
import sys

EMPTY_STATE = np.full((10), 12)


class ReplEnv(Env):
    action_space = Discrete(4)  # write 1, write +, write -, run
    act_code_map = ['1', '+', '-', 'clear']
    current_code = ''

    observation_space = Box(0, 12, shape=(10, 0), dtype=int)
    state = EMPTY_STATE.copy()
    stdout_state_map = dict({'-': 10, 'E': 11, ' ': 12}, **{str(i): i for i in range(10)})
    state_stdout_map = dict((reversed(item) for item in stdout_state_map.items()))

    def __init__(self):
        self.metadata = {'render.modes': ['human']}

    @staticmethod
    def _remove_newline(s, maxlen):
        return s[:maxlen + 1][:-1]

    def _run_expression(self, expr):
        old = sys.stdout
        stdout = StringIO()
        sys.stdout = stdout
        try:
            exec('print({0})'.format(expr))
        except SyntaxError:
            sys.stdout = old
            return 'E'
        sys.stdout = old
        return self._remove_newline(stdout.getvalue(), 10)

    def _format_output(self, stdout_str):
        new_state = EMPTY_STATE.copy()
        for i, char in enumerate(stdout_str):
            new_state[i] = self.stdout_state_map[char]
        return new_state

    def _run_code(self):
        stdout_str = self._run_expression(self.current_code)
        self.state = self._format_output(stdout_str)

    def step(self, action):
        code_token = self.act_code_map[action]
        if code_token == 'clear':
            self.current_code = ''
        elif len(self.current_code) >= 10:
            self.current_code = ''
        else:
            self.current_code += code_token
        self._run_code()
        reward = 0
        info = {}
        done = False
        return self.state, reward, done, info

    def render(self, mode='human'):
        outfile = sys.stdout
        inp = '>>> ' + self.current_code
        outfile.write(inp + '\n')
        out = ''.join([state_stdout_map[i] for i in self.state])
        outfile.write(out + '\n')

    def reset(self):
        self.current_code = ''
        self.state = EMPTY_STATE.copy()
        return self.state
