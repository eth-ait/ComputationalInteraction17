# PLEASE NOTE THAT THIS IS NOT ALL THE CODE USED WITHIN THE FIRST TUTORIAL, SEE TUTORIAL FOR FULL CODE.

import numpy as np
import random
import matplotlib.pyplot as plt


def __init__(self):

    self.deck_values = [0, 1, 2, 3]

    random.shuffle(self.deck_values)  # randomise deck order

    self.num_draws = [0, 0, 0, 0]  # set up list for tracking number of draws
    self.est_values = [0, 0, 0, 0]  # set up list for tracking estimated values

def calc_reward(self, deck_to_draw):

    deck_number = self.deck_values[deck_to_draw]  # the deck number to draw from

    good = 0  # if the deck is good or bad

    rand_num = random.random()  # random float between 0.0 and 1.0

    if deck_number == 0:  # average over 10 draws, -250

        good = -1  # bad deck

        if rand_num < 0.5:
            reward = -150
        else:
            reward = 100

    elif deck_number == 1:  # average over 10 draws, -250

        good = -1  # bad deck

        if rand_num < 0.1:
            reward = -700
        else:
            reward = 50

    elif deck_number == 2:  # average over 10 draws, +200

        good = 1  # good deck

        if rand_num < 0.5:
            reward = -35
        else:
            reward = 75

    elif deck_number == 3:  # average over 10 draws, +250

        good = 1  # good deck

        if rand_num < 0.1:
            reward = -200
        else:
            reward = 50

    return reward, good

# choose which deck to draw from
def choose_eps_greedy(self, epsilon):  

    # generate a random float between 0.0 and 1.0
    rand_num = random.random()  

    # get best deck
    best_deck = np.argmax(self.est_values)

    # if the random number is higher than epsilon, exploit
    if rand_num > epsilon:  
        
        return best_deck  
    
    # if random number is lower than epsilon, explore
    else:
        random_deck = random.choice(self.deck_values)
        
        # make sure random deck chosen is not best deck
        while random_deck == best_deck:
            random_deck = random.choice(self.deck_values)

        return random_deck 

def update_est(self, deck_to_draw, reward):

    # increase number of deck draws by one
    self.num_draws[deck_to_draw] += 1  
    
    # calculate the step-size
    alpha = 1./self.num_draws[deck_to_draw] 
    
    # running average of rewards
    self.est_values[deck_to_draw] += alpha * (reward - self.est_values[deck_to_draw])  

def experiment(self, num_draws_wanted, epsilon, block_size):

    history = []
    results = []
    running_total = 0

    for n in range(num_draws_wanted):

        deck_to_draw = self.choose_eps_greedy(epsilon)  # choose which deck to draw from
        (reward, good_draw) = self.calc_reward(deck_to_draw)  # calculate the reward from drawing
        self.update_est(deck_to_draw, reward)  # update deck value estimates
        history.append(good_draw)  # store reward value

    for n in range(len(history)):

        if n%block_size == 0:  # if at the start of a new block
            results.append(running_total)  # append the number of net good draws to results
            running_total = 0  # reset running total to zero

        running_total += history[n]

    return results