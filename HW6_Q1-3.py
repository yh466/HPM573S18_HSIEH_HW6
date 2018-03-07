# HPM573 HW6

import numpy as np
import scr.FigureSupport as Fig
import scr.SamplePathClass as PathCls
import scr.StatisticalClasses as Stat


class Game(object):
    def __init__(self, id, prob_head):
        """
        initiates a game
        :param id: ID of the game
        :param prob_head: probability of head in a coin flip (must be in [0,1])
        """
        self._id = id
        self._rnd = np.random       # random number generator for this game
        self._rnd.seed(id)          # specifying the seed of random number generator for this game

        self._probHead = prob_head  # probability of flipping a head
        self._countWins = 0         # number of wins, set to 0 to begin
        self._reward = 0            # initialize reward
        self._reward_owner = 0      # initialize reward for the owner
        self._loss = 0              # initialize the index - will take on value 0 or 1

    def simulate(self, n_of_flips):

        count_tails = 0             # number of consecutive tails so far, set to 0 to begin

        # flip the coin 20 times
        for i in range(n_of_flips):

            # in the case of flipping a heads
            if self._rnd.random_sample() < self._probHead: #rnd.random() return the next floating point number in the range [0.0, 1.0)
                if count_tails >= 2:  # if the series is ..., T, T, H
                    self._countWins += 1  # increase the number of wins by 1
                count_tails = 0  # the tails counter needs to be reset to 0 because a heads was flipped

            # in the case of flipping a tails
            else:
                count_tails += 1  # increase tails count by one

    def get_reward(self):
        # calculate the reward from playing a single game
        self._reward = 100*self._countWins - 250
        return self._reward

    def get_reward_owner(self):
        self._reward_owner = 250 - 100*self._countWins
        return self._reward_owner

    def index_loss(self):
        # to index the outcome of a game
        if self._reward >= 0:
            self._loss = 0
        elif self._reward < 0:
            self._loss = 1
        return self._loss


class SetOfGames:
    def __init__(self, id, prob_head, n_games):
        """create a set of games"""
        self._id = id
        self._gameRewards = []       # create an empty list where rewards will be stored
        self._gameRewardsOwner = []  # create an empty list where we store rewards for the owner
        self._gameLoss = []          # create an empty list where loss index will be stored

        # simulate the games and populate the set of games
        for n in range(n_games):
            # create a new game
            game = Game(id=n, prob_head=prob_head)
            # simulate the game with 20 flips
            game.simulate(20)
            # store the reward
            self._gameRewards.append(game.get_reward())
            # store the reward for the owner
            self._gameRewardsOwner.append(game.get_reward_owner())
            # store the outcome (losing or winning)
            self._gameLoss.append(game.index_loss())

    def simulate(self):
        return GameSetOutcomes(self)

    def get_rewards(self):
        """returns the rewards of each game in this game set"""
        return self._gameRewards

    def get_rewards_owner(self):
        return self._gameRewardsOwner

    def get_losses(self):
        """returns winning(0) or losing(1) in this game set"""
        return self._gameLoss


class GameSetOutcomes:
    def __init__(self, simulated_set):
        """extract outcomes of a simulated set of games"""
        self._simulatedGameSet = simulated_set

        # summary statistics on game outcomes (rewards and losses)
        self._sumStat_gameRewards = Stat.SummaryStat('Game rewards',self._simulatedGameSet.get_rewards())
        self._sumStat_gameRewardsOwner = Stat.SummaryStat('Owner reward',self._simulatedGameSet.get_rewards_owner())
        self._sumStat_gameLosses = Stat.SummaryStat('Game losses', self._simulatedGameSet.get_losses())

    def get_reward_list(self):
        """ returns all the rewards from all game to later be used for creation of histogram """
        return self._simulatedGameSet.get_rewards()

    def get_reward_list_owner(self):
        return self._simulatedGameSet.get_rewards_owner()

    def get_ave_reward(self):
        """ returns the average reward from all games"""
        return self._sumStat_gameRewards.get_mean()

    def get_CI_of_ave_reward(self,alpha):
        """returns the confidence interval of the average rewards of the set of games"""
        return self._sumStat_gameRewards.get_t_CI(alpha)

    def get_ave_reward_owner(self):
        return self._sumStat_gameRewardsOwner.get_mean()

    def get_CI_of_ave_reward_owner(self, alpha):
        return self._sumStat_gameRewardsOwner.get_t_CI(alpha)

    def get_probability_loss(self):
        """ returns the probability of a loss """
        return self._sumStat_gameLosses.get_mean()

    def get_CI_of_probability_loss(self,alpha):
        """returns the CI of the probability of a loss"""
        return self._sumStat_gameLosses.get_t_CI(alpha)


class MultiSet:
    """simulates multiple sets of games"""
    def __init__(self, ids, prob_head, n_games):
        """
        :param ids: a list of ids for game sets to simulate
        :param prob_head: a list of probability of getting head, same for all game sets here
        :param n_games: a list of number of games in game sets to simulate
        """

        self._ids = ids
        self._gamesetSizes = n_games
        self._headProbs = prob_head

        self._gameRewards = []  # create an empty list where rewards will be stored
        self._meanRewards = []  # create an empty list to store the mean reward for each simulated set
        self._sumStat_meanRewards = None

    def simulate(self):
        """simulates all game sets"""

        for i in range(len(self._ids)):
            # create a new game set
            setofgames = SetOfGames(self._ids[i], self._headProbs[i], self._gamesetSizes[i])
            # simulate the game with 20 flips
            out = setofgames.simulate()
            # store the reward
            self._gameRewards.append(setofgames.get_rewards())
            self._meanRewards.append(out.get_ave_reward())

        # after simulating all game sets
        # summary statistics of mean rewards and probability of losing money

        self._sumStat_meanRewards = Stat.SummaryStat('Mean rewards', self._meanRewards)

    def get_all_mean_rewards(self):
        """returns a list of mean rewards for all simulated sets"""
        return self._meanRewards

    def get_overall_mean_reward(self):
        """returns the mean of the mean reward of all sets"""
        return self._sumStat_meanRewards.get_mean()

    def get_CI_mean_reward(self,alpha):
        return self._sumStat_meanRewards.get_t_CI(alpha)

    def get_PI_mean_reward(self,alpha):
        return self._sumStat_meanRewards.get_PI(alpha)


PROB_HEAD = 0.5
SIM_SET_NUM = 1000   # number of simulated cohorts used for making projections
SIM_GAME_NUM1 = 1000
SIM_GAME_NUM2 = 10   # size of the real cohort to make the projections for
ALPHA = 0.05

# HW6 Problem 1:
myGames = SetOfGames(id=1, prob_head=PROB_HEAD, n_games=SIM_GAME_NUM1)
gameOutcomes = myGames.simulate()

print("Problem 1")
print("The average expected reward is:", gameOutcomes.get_ave_reward())
print("Based on 1000 simulations, the 95% t-based CI for the expected reward is",
      gameOutcomes.get_CI_of_ave_reward(ALPHA))
print("The average probability of losing money is:",gameOutcomes.get_probability_loss())
print("Based on 1000 simulations, the 95% t-based CI for the probability of loss is",
      gameOutcomes.get_CI_of_probability_loss(ALPHA))

print("                                                           ")
# HW6 Problem 2:

print("Problem 2")
print("If the game was repeated many times, on average 95% of the time, "
      "the confidence intervals created for the average game reward would cover the true average game reward.")
print("If the game was repeated many times, on average 95% of the time, "
      "the confidence intervals created for the probability of losing money in a game would cover the true probability.")

print("                                                           ")
# HW6 Problem 3:
myGames = SetOfGames(id=1, prob_head=PROB_HEAD, n_games=SIM_GAME_NUM1)
gameOutcomes = myGames.simulate()
print("Problem 3")
print("For the owner who gets to play this game many times, the expected reward is",
      gameOutcomes.get_ave_reward_owner(),
      gameOutcomes.get_CI_of_ave_reward_owner(ALPHA), ".")
print("We are 95% confident that this confidence interval would coverage the true average of the expected reward "
      "because when we get to play the game many times, "
      "95% of the confidence interval generated would cover the true mean.")

gamblerSets = MultiSet(ids=range(SIM_SET_NUM), prob_head=[PROB_HEAD]*SIM_SET_NUM, n_games=[SIM_GAME_NUM2]*SIM_SET_NUM)
gamblerSets.simulate()

print("For gamblers who gets to play this game only 10 times, the expected mean reward is",
      gamblerSets.get_overall_mean_reward(),
      "with a projection interval of",
      gamblerSets.get_PI_mean_reward(ALPHA), ".")
print("With a 95% probability, we expect this game reward to fall in this projection interval.")