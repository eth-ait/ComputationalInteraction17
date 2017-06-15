# PLEASE NOTE THAT THIS IS NOT ALL THE CODE USED WITHIN THE SECOND TUTORIAL, SEE TUTORIAL FOR FULL CODE.

import numpy as np
import random
import matplotlib.pyplot as plt


def __init__(self):

    # keep track of current state
    self.current_state = -1

    # array for storing reward values
    self.r = np.array([[-1,  -10,  -30,   -1],   # State S0
                       [-1,   -1,  -30,   90],   # State S1
                       [-1,   -1,   -1,   -1],   # State S2
                       [-1,   -1,   -1,   -1]])  # State S3

    # array for storing q values
    self.q = np.zeros_like(self.r)

    # keep track of total reward received
    self.total_distal_reward = 0.0

    # keep track of if we in the proximal state
    self.proximal = 0

    # keep track of rewards after proximal state
    self.total_proximal_reward = 0.0

def get_available_actions(self):

    # get the row of rewards for the current state
    current_reward_row = self.r[self.current_state]

    # get the states which are possible to transition to
    current_available_actions = np.where(current_reward_row != -1)[0]

    return current_available_actions

def choose_next_action(self, available_actions, epsilon):

    # first calculate best action

    # used to hold the q values of possible moves
    possible_q_list = np.zeros(len(self.q[self.current_state]))

    # set each of the elements to 'None'
    for x in range(len(possible_q_list)):
        possible_q_list[x] = None

    # where a move is possible, add the Q-value to possible_q_list
    possible_q_list[available_actions] = self.q[self.current_state, available_actions]

    # possible_q_list contains the Q-values for moves from that state which are possible

    # the moves with the largest Q-values, ignoring 'None'
    best_action_list = np.where(possible_q_list == np.nanmax(possible_q_list))[0]

    print "Best action list ", best_action_list

    # choose a best action randomly in case there are multiple
    best_action = random.choice(best_action_list)

    # generate random float between 0 and 1
    rand_num = random.random()

    # if greater than epsilon, return best action
    if rand_num > epsilon:

        print "Exploit: ", best_action
        return best_action

    # else, return a random other action
    else:
        random_action = random.choice(available_actions)

        while random_action == best_action:
            random_action = random.choice(available_actions)

        print "Explore: ", random_action
        return random_action

def calculate_max_q_value(self, action):

    # get the max q value of the next state
    max_value = np.amax(self.q[action])

    return max_value

def update_q(self, action, alpha, gamma):

    # current q value
    current_q = self.q[self.current_state, action]

    print "Current Q-value: ", current_q

    # current reward value
    current_r = self.r[self.current_state, action]

    print "Reward received: ", current_r

    # total reward received
    self.total_distal_reward += current_r

    if self.proximal == 1:

        self.total_proximal_reward += current_r

    # max q value at next state
    max_q_value = self.calculate_max_q_value(action)

    print "Max Q value in next state: ", max_q_value

    # update current q value
    self.q[self.current_state][action] = current_q + alpha * (current_r + gamma * max_q_value - current_q)

    print "Updated Q value table: "

    print self.q

def run_experiment(self, initial_state, alpha, gamma, epsilon, num_rewarded_runs_wanted):

    # counter for number of runs
    num_rewarded_runs = 0
    num_runs = 0
    num_proximal_runs = 0
    self.current_state = initial_state

    total_distal_reward_array = np.array([])
    total_proximal_reward_array = np.array([])

    while num_rewarded_runs < num_rewarded_runs_wanted:

        print ""
        print "Run number: ", num_runs

        # if a terminal state is reached, reset to intial state, and increment counter
        if self.current_state == 2 or self.current_state == 3:

            num_runs += 1

            if self.current_state == 3:

                num_rewarded_runs += 1

                total_distal_reward_array = np.append(total_distal_reward_array,
                                                      self.total_distal_reward / (80 * num_runs))

                total_proximal_reward_array = np.append(total_proximal_reward_array,
                                                      self.total_proximal_reward / (90 * num_proximal_runs))

            self.current_state = initial_state

            self.proximal = 0

        print "Current state: ", self.current_state

        # get available action
        available_actions = self.get_available_actions()
        print "Available actions: ", available_actions

        # pick action from available actions
        action_chosen = self.choose_next_action(available_actions, epsilon)
        print "Action chosen ", action_chosen

        # update q matrix
        self.update_q(action_chosen, alpha, gamma)

        # current state becomes the new chosen state
        self.current_state = action_chosen

        if self.current_state == 1:

            num_proximal_runs += 1

            self.proximal = 1

    print "\nFinal Q Matrix"
    print self.q

    plt.figure()
    plt.plot(total_distal_reward_array, label="Expected Reward (Distal)", color='orange')  # distal == total
    plt.draw()
    plt.ylim(0, 1)  # limits for the y-axis
    plt.legend(loc='best')  # display the graph key
    plt.savefig('distal_graph.png')  # save graph to folder

    plt.figure()
    plt.plot(total_proximal_reward_array, label="Expected Reward (Proximal)", color = 'orange')
    plt.draw()
    plt.ylim(0, 1)  # limits for the y-axis
    plt.legend(loc='best')  # display the graph key
    plt.savefig('proximal_graph.png')  # save graph to folder

    plt.show()  # display the graph

def check_training(self):
    self.current_state = 0
    steps = [self.current_state]

    while self.current_state != 2 and self.current_state != 3:

        best_action_list = np.where(self.q[self.current_state] == np.amax(self.q[self.current_state]))[0]

        best_action = random.choice(best_action_list)

        steps.append(best_action)
        self.current_state = best_action

    # Print selected sequence of steps
    print("Selected path:")
    print(steps)
