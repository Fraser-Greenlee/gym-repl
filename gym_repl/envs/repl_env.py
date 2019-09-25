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

    observation_space = Box(0, 12, shape=(1, 10), dtype=int)
    state = EMPTY_STATE.copy()
    stdout_state_map = dict({'-': 11, ' ': 12, 'E': 13}, **{str(i): i for i in range(10)})
    state_stdout_map = dict((reversed(item) for item in stdout_state_map.items()))

    def __init__(self):
        self.metadata = {'render.modes': ['human']}

    def _remove_newline(s, maxlen):
        return s[:maxlen + 1][:-1]

    def _format_output(stdout):
        out = _remove_newline(stdout, 10)
        new_state = EMPTY_STATE.copy()
        for i, char in enumerate(out):
            new_state[i] = stdout_state_map[char]
        return new_state

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
        return self._format_output(stdout.getvalue())

    def _run_code(self):
        self.state = self._run_expression(self.current_code)

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
