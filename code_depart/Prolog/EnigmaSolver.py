from swiplserver import PrologMQI


class EnigmaSolver:
    def __init__(self):
        self._env = None
        self._crystals_prolog_kb = ""

    def set_enigma_state(self, door_state):
        self._env = door_state
        crystals = []
        for crystal in self._env[0][1:]:
            if crystal != '':
                crystals.append(crystal)
        self._crystals_prolog_kb = "consult('Prolog/{num_crystals}Crystals.pl').".format(num_crystals=len(crystals))

    def solve_enigma(self):
        with PrologMQI() as mqi:
            with mqi.create_thread() as prolog_thread:
                prolog_thread.query(self._crystals_prolog_kb)
                door_env = "[{env_value}]".format(env_value=",".join(self._env[0]))
                result = prolog_thread.query("obtainKey({env}, Res" + ").".format(env=door_env))

        if isinstance(result[0]["Res"], list):
            key_numerical = result[0]["Res"][-1]
            key_numerical_strs = ["first","second","third","fourth","five","sixth"]
            key = key_numerical_strs[key_numerical - 1]
        else:
            key = result[0]["Res"]
        return key