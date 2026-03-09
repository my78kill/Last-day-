import random
from roles import ROLES, get_team

class GameSession:

    def __init__(self, chat_id):

        self.chat_id = chat_id
        self.players = {}
        self.roles = {}
        self.alive = set()
        self.votes = {}

    def add_player(self,user_id,name):

        if user_id in self.players:
            return False

        self.players[user_id] = name
        self.alive.add(user_id)

        return True

    def distribute_roles(self):

        role_list = list(ROLES.keys())

        for uid in self.players:

            role = random.choice(role_list)

            self.roles[uid] = role

    def vote(self,voter,target):

        self.votes[voter] = target

    def resolve_votes(self):

        if not self.votes:
            return None

        counts = {}

        for t in self.votes.values():

            counts[t] = counts.get(t,0)+1

        eliminated = max(counts,key=counts.get)

        if eliminated in self.alive:

            self.alive.remove(eliminated)

        self.votes.clear()

        return eliminated

    def check_win(self):

        virus = 0
        survivor = 0

        for uid in self.alive:

            role = self.roles[uid]

            if get_team(role).value == "Virus":
                virus += 1
            else:
                survivor += 1

        if virus == 0:
            return "Survivors"

        if virus >= survivor:
            return "Virus"

        return None