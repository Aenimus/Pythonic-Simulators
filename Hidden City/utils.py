from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from Encounter import Combat
    from PlayerState import PlayerState

verbose: bool = False

hidden_city = {1: "The Hidden Apartment",
               2: "The Hidden Office",
               3: "The Hidden Hospital",
               4: "The Hidden Alley",
               5: "the ancient amulet"}

locs = 0

def agreement(monster: "Combat") -> str:
    if monster.group:
        return "some"
    return "a"

def log(message: str) -> None:
    print(message)

def vlog(message: str) -> None:
    if verbose:
        log(message)

def unlock(player_state: "PlayerState") -> None:
    locs = player_state.tracking
    if locs < 1:
        log(f"Atique machete acquired. Using 1 adventure to unlock {hidden_city[1]}.")
    else:
        log(f"{hidden_city[locs]} completed. Using 1 adventure to unlock {hidden_city[locs + 1]}.")
    player_state.tracking += 1
