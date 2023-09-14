from swiplserver import PrologMQI


class EnigmaSolver:
    def __init__(self):
        self.env = None
        self.number_of_cristals = None
        self.lock_color = None
        self.crystals = []
        self.three_crystals_prolog_kb = "consult('Prolog/3Crystals.pl')."
        self.four_crystals_prolog_kb = "consult('Prolog/4Crystals.pl')."
        self.five_crystals_prolog_kb = "consult('Prolog/5Crystals.pl')."
        self.six_crystals_prolog_kb = "consult('Prolog/6Crystals.pl')."
        self.keys_numericals = {}
        self.keys_numericals[1] = "first"
        self.keys_numericals[2] = "second"
        self.keys_numericals[3] = "third"
        self.keys_numericals[4] = "fourth"
        self.keys_numericals[5] = "five"
        self.keys_numericals[6] = "sixth"

    def __set_enigma_state__(self, door_state):
        if len(door_state) != 0:
            self.env = door_state
            self.lock_color = door_state[0][0]
            i = 0
            self.crystals = []
            for crystals in door_state[0]:
                if i != 0 and crystals != '':
                    self.crystals.append(crystals)
                i = i + 1
            self.number_of_cristals = len(self.crystals)

    def __solve_enigma__(self):

        with PrologMQI() as mqi:
            with mqi.create_thread() as prolog_thread:
                if self.number_of_cristals == 3:
                    prolog_thread.query(self.three_crystals_prolog_kb)
                if self.number_of_cristals == 4:
                    prolog_thread.query(self.four_crystals_prolog_kb)
                if self.number_of_cristals == 5:
                    prolog_thread.query(self.five_crystals_prolog_kb)
                if self.number_of_cristals == 6:
                    prolog_thread.query(self.six_crystals_prolog_kb)

                env_str = "[" + self.lock_color + ","
                i = 0
                for elem in self.crystals:
                    if i != (len(self.crystals) - 1):
                        env_str = env_str + elem + ","
                    else:
                        env_str = env_str + elem
                    i = i + 1
                env_str = env_str + "]"
                result = prolog_thread.query("obtainKey(" + env_str + ", Res" + ").")

        if isinstance(result[0]["Res"], list):
            key_numerical = result[0]["Res"][len(result[0]["Res"]) - 1]
            key = self.keys_numericals[key_numerical]
        else:
            key = result[0]["Res"]
        return key
