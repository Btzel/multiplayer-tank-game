def make_decision(previous_state,player_health,player_gold,enemy_count,teammate_count,coins_nearby):
    
    state = previous_state
    if((state != "heal" and state != "shoot and heal")):
        if enemy_count > 0:
            if(player_health < 50):
                if(player_gold < 30 and coins_nearby):
                    state = "collect"
                elif(player_gold < 30 and not coins_nearby):
                    state = "evade"
                elif(player_gold < 60 and player_health < 20):
                    state = "heal"
                elif(player_gold < 60 and coins_nearby):
                    state = "shoot and collect"
                elif(player_gold < 60 and not coins_nearby):
                    state = "shoot and heal"
                elif(player_gold >= 60):
                    state = "shoot and heal"
            elif(enemy_count > teammate_count + 1):
                if(player_gold > 30):
                    state = "shoot and evade"
                else:
                    state = "evade"
            elif(enemy_count <= teammate_count + 1):
                if(player_gold <= 30 and coins_nearby):
                    state = "shoot and collect"
                else:
                    state = "shoot and follow"
            elif(player_gold > 100):
                if(coins_nearby):
                    state = "shoot and collect"
                else:
                    state = "shoot and follow"
        elif player_health < 70:
            if(player_gold < 50 and coins_nearby):
                state = "collect"
            else:
                state = "heal"
        elif player_gold < 500 and coins_nearby:
            state = "collect"
        else:
            state = "traverse"
    else:
        if(player_health < 100 and player_gold > 0):
            state = state
        else:
            state = "collect"
                
    
    return state
def decision_messenger(previous_state,player_health,player_gold,enemy_count,teammate_count,coins_nearby):

    if(player_health is not None and player_gold is not None and enemy_count is not None and teammate_count is not None and coins_nearby is not None):

        print()
        print(f"Player health: {player_health}")
        print(f"Player gold: {player_gold}")
        print(f"Enemy count: {enemy_count}")
        print(f"Teammate count: {teammate_count}")
        print(f"Coins nearby: {coins_nearby}")
        print()
    
        decision = make_decision(previous_state,player_health,player_gold,enemy_count,teammate_count,coins_nearby)
        print("Decision: ", decision,"!")
        return decision
    else:
        print(player_health) if not None else print("player health is None")
        print(player_gold) if not None else print("player gold is None")
        print(enemy_count) if not None else print("enemy count is None")
        print(teammate_count) if not None else print("teammate count is None")
        print(coins_nearby) if not None else print("coins nearby is None")
        
        decision = None
        print("Decision: ", decision,"!")
        return decision
        