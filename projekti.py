
import requests
import os
from dotenv import load_dotenv
load_dotenv()

#https://koodipahkina.monad.fi/app/docs

def createGame(token: str, API:str):

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    data = {}

    response = requests.post(API, json=data, headers=headers)

    if response.status_code == 200:
        game_info = response.json()
        print('New game created!')
        return game_info
    else:
        print('Something went wrong!')
        return response.status_code

# To give action, take or pay, must have game id :)
def cardAction(game_id:str, action:bool):
    token = os.getenv("TOKEN")
    API = os.getenv("API")

    cardActionApi = f"{API}/{game_id}/action"

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    data = {
         "takeCard": action
    }

    response = requests.post(cardActionApi, json=data, headers=headers)
    game_status = response.json()
    
    return game_status


def main():
    for _ in range(1): # Change match amount here
        token = os.getenv("TOKEN")
        API = os.getenv("API")

        #Create game and get game ID
        new_game_info = createGame(token, API)
        game_id = new_game_info.get('gameId')

        #First card and money from creating the game
        first_card = new_game_info.get('status').get('card')
        card_money = new_game_info.get('status').get('money')
        card_value = first_card - card_money
        #When creating the game we do one action, checking that its not too high
       
        if first_card < 15 or  card_value < 10 :
            game = cardAction(game_id, True)
            print("Took the card")
        else:
            game = cardAction(game_id, False)
            print("Skip!")
        print(game)
        
        #We use the amount of cards left to loop each game!
        cardsLeft = game.get('status').get('cardsLeft')
        ## card action loop ## 
        while cardsLeft > 0:
            
            #No money
            if game.get('message') == 'Cannot pass without money':
                    game = cardAction(game_id, True)
                    print('No money')

            #Error handeling for getting card and money values = calcualting them
            try:
                current_card = game.get('status').get('card')
                card_money = game.get('status').get('money')
                card_value = current_card - card_money
            except AttributeError:
                break
            except TypeError:
                break
       
            # taking slightly less than half of stack (15) and card value (card - money) less than 10
            # Safe game to win good amount
            if current_card < 15 and card_money > 10 or  card_value < 10 :
                game = cardAction(game_id, True)
                print("Took the card")
                    
            try:
                cards = game.get('status').get('players')[0].get('cards')
            except AttributeError:
                break
            
            pair_found = False

            # loop each player card and check if it stacks (one smaller or larger)
            for card_row in cards:
                for card in card_row:
                    if card == current_card + 1 or card == current_card - 1:
                        cardAction(game_id, True)
                        pair_found = True
                        print('was pair')
                        break
                if pair_found:
                    break

            game = cardAction(game_id, False) # At last skip if nothig else matches

            print(game.get('status'))
            print('Skip')

if __name__ == "__main__":
        main()
