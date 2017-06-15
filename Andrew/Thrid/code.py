# PLEASE NOTE THAT THIS IS NOT ALL THE CODE USED WITHIN THE THIRD TUTORIAL, SEE TUTORIAL FOR FULL CODE.

import numpy as np
import random
import matplotlib.pyplot as plt

np.set_printoptions(suppress=True)


def __init__(self):

    # array for storing reward values
    self.r = np.array([[-1, -10, -30,  -1],   # State S0
                       [-1,  -1, -30,  90],   # State S1
                       [-1,  -1,  -1,  -1],   # State S2
                       [-1,  -1,  -1,  -1]])  # State S3

    # current reward
    self.reward = -1

    # keep track of total reward
    self.total_reward = 0.0

    # list of states
    self.state_list = [0, 1, 2, 3]

    # belief state, all same to start
    self.belief_state = [0.3, 0.3, 0.3, 0.3]  # Choice to be made in s0 and s1

    # set up belief table
    self.belief_table = []

    for s0 in range(0, 11):
        for s1 in range (0, 11):
            for s2 in range (0, 11):
                for s3 in range (0, 11):
                    self.belief_table.append([s0, s1, s2, s3, 0, 0])

    # convert to array
    self.belief_table = np.vstack(self.belief_table)

    # divide all by 10
    self.belief_table = self.belief_table/10.0

    # index of belief table corresponding to belief state
    self.belief_table_index = -1

    # index of belief table corresponding to previous belief state
    self.previous_belief_table_index = -1

    # keep track of real state
    self.real_state = -1

    # action number: 0 = Pull lever, 1 = Enter magazine
    self.action_number = -1

    # state to move to next
    self.next_state = -1

    # list to keep track of expected value
    self.expected_value_array = []

def reset(self, initial_state):

    print "Reset"

    self.belief_state = [0.3, 0.3, 0.3, 0.3]
    self.real_state = initial_state

def observe(self, observation_chance):

    rand_num = random.random()
    if rand_num < observation_chance:
        return self.real_state
    else:
        random_state = random.choice(self.state_list)

        while random_state == self.real_state:
            random_state = random.choice(self.state_list)

        return random_state

def update_belief_state(self, observation_state, observation_chance):

    # Temporary list
    temp_belief_state = [0.0, 0.0, 0.0, 0.0]

    # Use Bayes' Rule to update belief state
    for n in range(len(temp_belief_state)):
        if observation_state == n:
            temp_belief_state[n] = observation_chance * self.belief_state[n]
        else:
            temp_belief_state[n] = ((1 - observation_chance) / (len(self.state_list) - 1)) * self.belief_state[n]

    # Normalise so the belief state sums to 1
    temp_total = sum(temp_belief_state)
    self.belief_state = list(n / temp_total for n in temp_belief_state)

    # Round to 1 decimal place
    self.belief_state = [round(n, 1) for n in self.belief_state]

def choose_next_action(self, epsilon):

    # get the q_values of the two actions
    q_value_a0 = (self.belief_table[self.belief_table_index, 4])

    q_value_a1 = (self.belief_table[self.belief_table_index, 5])

    # choose an action using epsilon greedy
    rand_num = random.random()

    if q_value_a0 > q_value_a1:

        if rand_num > epsilon:
            self.action_number = 0  # Exploit

        else:
            self.action_number = 1  # Explore

    elif q_value_a1 > q_value_a0:

        if rand_num > epsilon:
            self.action_number = 1  # Exploit

        else:
            self.action_number = 0  # Explore

    else:
        self.action_number = random.randint(0, 1)

# get corresponding next state from current state and action number
def get_next_state(self):

    if self.real_state == 0:

        if self.action_number == 0:

            self.next_state = 1

        elif self.action_number == 1:

            self.next_state = 2

    elif self.real_state == 1:

        if self.action_number == 0:

            self.next_state = 2

        elif self.action_number == 1:

            self.next_state = 3

def get_belief_table_index(self):

    self.belief_table_index = np.where((self.belief_table[:, 0] == self.belief_state[0])
                                       & (self.belief_table[:, 1] == self.belief_state[1])
                                       & (self.belief_table[:, 2] == self.belief_state[2])
                                       & (self.belief_table[:, 3] == self.belief_state[3]))[0]

# get highest Q-value in belief state
def calculate_max_q_value(self):

    # get the Q-values of the two actions
    q_value_a0 = self.belief_table[self.belief_table_index, 4]

    q_value_a1 = self.belief_table[self.belief_table_index, 5]

    # return the highest
    if q_value_a0 > q_value_a1:
        return q_value_a0
    else:
        return q_value_a1

def update_belief_table(self, alpha, gamma):

    # get correct element index for the select action
    if self.action_number == 0:
        location = 4
    else:
        location = 5

    max_q_value = self.calculate_max_q_value()

    previous_q = self.belief_table[self.previous_belief_table_index, location]

    print "Real state: ", self.real_state
    print "Action number: ", self.action_number
    print "Max Q: ", max_q_value
    print "Reward: ", self.reward

    print "Before update: ", self.belief_table[self.previous_belief_table_index]

    # update Q-value
    self.belief_table[self.previous_belief_table_index, location] = previous_q + alpha * (self.reward + gamma * max_q_value - previous_q)

    # round to 1 decimal place
    self.belief_table[self.previous_belief_table_index, location] = round(self.belief_table[self.previous_belief_table_index, location], 1)

    print "After update: ", self.belief_table[self.previous_belief_table_index]

def run_experiment(self, initial_state, observation_chance, alpha, gamma, epsilon, num_runs_wanted):

    # set current state to initial state wanted
    self.real_state = initial_state

    # make an initial run

    # make an observation
    observation = self.observe(observation_chance)

    # update belief state with observation
    self.update_belief_state(observation, observation_chance)

    # get the corresponding index in the belief table
    self.get_belief_table_index()

    # choose next action
    self.choose_next_action(epsilon)

    # get the next state
    self.get_next_state()

    # get the reward for moving from current state to next state
    self.reward = self.r[self.real_state][self.next_state]

    # update total reward
    self.total_reward += self.reward

    # move to the next state
    self.real_state = self.next_state
    self.belief_state = [0.3, 0.3, 0.3, 0.3]

    print "Real state update: ", self.real_state, " --> ", self.next_state

    # variables to keep track
    num_rewards_received = 0
    num_fails = 0

    num_runs = 0

    while num_runs < num_runs_wanted:

        print ""

        # make an observation
        observation = self.observe(observation_chance)

        # update belief state with observation
        self.update_belief_state(observation, observation_chance)

        # keep track of the previous belief_table_index
        self.previous_belief_table_index = self.belief_table_index

        # get the corresponding index in the belief table
        self.get_belief_table_index()

        print "Observation: ", observation

        # update the belief table using Q-learning
        self.update_belief_table(alpha, gamma)

        # if terminal state reached
        if self.real_state == 2 or self.real_state == 3:

            if self.real_state == 2:
                num_fails += 1
            elif self.real_state == 3:
                num_rewards_received += 1

            num_runs += 1

            self.expected_value_array = np.append(self.expected_value_array, self.total_reward / (80 * num_runs))

            # reset to inital values
            self.reset(initial_state)

            # make an observation
            observation = self.observe(observation_chance)

            # update belief state with observation
            self.update_belief_state(observation, observation_chance)

            print "Observation: ", observation

            # get the corresponding index in the belief table
            self.get_belief_table_index()

            # keep track of the previous belief_table_index
            self.previous_belief_table_index = self.belief_table_index

        # choose next action
        self.choose_next_action(epsilon)

        # get the next state
        self.get_next_state()

        # get the reward for moving from current state to next state
        self.reward = self.r[self.real_state][self.next_state]

        # update total reward
        self.total_reward += self.reward

        print "Real state update: ", self.real_state, " --> ", self.next_state

        # move to the next state
        self.real_state = self.next_state
        self.belief_state = [0.3, 0.3, 0.3, 0.3]

    print ""
    print "Number of fails:"
    print num_fails

    print ""
    print "Number of rewards:"
    print num_rewards_received