from gym import Env
from gym.spaces import Discrete, Tuple
from numpy import inf
from six import StringIO
import sys


class ReplEnv(Env):
    metadata = {'render.modes': ['human']}
    action_space = Discrete(4)
    act_code_map = ['1', '+', '-', 'run']
    current_code = ''
    observation_space = Tuple(*[Discrete(13) for _ in range(10)])  # 0-9,-, ,E for length 10
    current_output = ' ' * 10
    output_obs_map = {'-': 11, ' ':12, 'E':13}
    output_obs_map = {str(i): i for i in range(10)}

    def __init__(self):
        super(ReplEnv, self).__init__()

    @staticmethod
    def _run_expression(expr):
        old = sys.stdout
        stdout = StringIO()
        sys.stdout = stdout
        try:
            exec('print({0})'.format(expr))
        except Exception:
            return 'E'
        sys.stdout = old
        return stdout.getvalue()[:10]

    def _run_code(self):
        self.current_output = self._run_expression(self.current_code)

    def step(self, action):
        code_token = act_code_map(action)
        if code_token == 'run':
            self.current_code = ''
            self._run_code()
        elif len(self.current_code) >= 10:
            self.current_code = ''
            self.current_output = 'E' 
        else:
            self.current_code += code_token
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
        inp = '>> ' + self.current_code
        outfile.write(inp + '\n')
        out = self.current_output
        outfile.write(out)

    def reset(self):
        self.current_code = ''
        self.current_output = ''
        obs = self._observe()
        return obs
