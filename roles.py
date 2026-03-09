from enum import Enum

class Team(Enum):
    VIRUS = "Virus"
    SURVIVOR = "Survivor"

ROLES = {
    "Infected": Team.VIRUS,
    "Mutant": Team.VIRUS,
    "Parasite": Team.VIRUS,
    "Doctor": Team.SURVIVOR,
    "Guardian": Team.SURVIVOR,
    "Scientist": Team.SURVIVOR,
    "Survivor": Team.SURVIVOR
}

def get_team(role):
    return ROLES.get(role)