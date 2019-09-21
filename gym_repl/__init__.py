from gym.envs.registration import register

register(
    id='repl-v0',
    entry_point='gym_repl.envs:ReplEnv',
)
