from gym import Env
from gym.spaces import Discrete, Box
from numpy import inf
from six import StringIO
import sys


class ReplEnv(Env):
    action_space = Discrete(4)  # write 1, write +, write -, run
    act_code_map = ['1', '+', '-', 'clear']
    current_code = ''

    observation_space = Box(0, 12, shape=(1, 10), dtype=int)
    current_output = ' ' * 10
    output_obs_map = {'-': 11, ' ': 12, 'E': 13}
    output_obs_map.update({str(i): i for i in range(10)})

    def __init__(self):
        self.metadata = {'render.modes': ['human']}

    @staticmethod
    def _run_expression(expr):
        old = sys.stdout
        stdout = StringIO()
        sys.stdout = stdout
        try:
            exec('print({0})'.format(expr))
        except SyntaxError:
            sys.stdout = old
            return 'E'
        sys.stdout = old
        return stdout.getvalue()[:11][:-1]

    def _run_code(self):
        self.current_output = self._run_expression(self.current_code)

    def step(self, action):
        code_token = self.act_code_map[action]
        if code_token == 'clear':
            self.current_code = ''
        elif len(self.current_code) >= 10:
            self.current_code = ''
        else:
            self.current_code += code_token
        self._run_code()
        obs = self.observe()
        reward = 0
        info = {}
        done = False
        return obs, reward, done, info

    def observe(self):
        return [
            self.output_obs_map[char] for char in self.current_output
        ]

    def render(self, mode='human'):
        outfile = sys.stdout
        inp = '>>> ' + self.current_code
        outfile.write(inp + '\n')
        out = self.current_output
        outfile.write(out + '\n')

    def reset(self):
        self.current_code = ''
        self.current_output = ''
        obs = self.observe()
        return obs
