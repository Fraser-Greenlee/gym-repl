from gym.envs.algorithmic import algorithmic_env
from six import StringIO
import sys


class ReplEnv(algorithmic_env.GridAlgorithmicEnv):
    def __init__(self, rows=2, base=1):
        super(ReplEnv, self).__init__(rows=rows, base=base, chars=False)

    @staticmethod
    def _run_code(code=''):
        old = sys.stdout
        stdout = StringIO()
        sys.stdout = stdout
        try:
            exec('print({0})'.format(code))
        except Exception:
            return 'E'
        sys.stdout = old
        return stdout.getvalue()

    def target_from_input_data(self, input_strings):
        curry = 0
        target = []
        for digits in input_strings:
            total = sum(digits) + curry
            target.append(total % self.base)
            curry = total // self.base

        if curry > 0:
            target.append(curry)
        return target
