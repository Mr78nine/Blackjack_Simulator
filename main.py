import os
from libs.playBj import State
from yaml import load, FullLoader
from time import time
import multiprocessing

cfg1 = open("Config/Basic_Strategy.yaml", 'r')
cfg2 = open("Config/hl2deck_0.yaml", 'r')
cfg3 = open("Config/Profbj_benchmark.yaml", 'r')
config1 = load(cfg1, Loader=FullLoader)
config2 = load(cfg2, Loader=FullLoader)
config3 = load(cfg3, Loader=FullLoader)


def task(iterations):
    wins = []
    for i in range(iterations):
        table = State(config1)

        start = table.playerBankroll
        bankruptAt = table.play_rounds(100)
        end = table.playerBankroll

        wins.append(end - start)
    return wins


#todo: House edge is, I think, units per 100 hands. If you win 1 unit per 100 hands on avg, then 1%
#todo: So find avg of the wins list, divide by len of wins list, then normalize it to per 100 hands

if __name__ == "__main__":
    ccount = multiprocessing.cpu_count()
    with multiprocessing.Pool(processes=ccount) as pool:
        multiprocessing.freeze_support()
        # task_arg_list = [config1 for i in range(ccount)]
        task_arg_list = [10000 for i in range(ccount)]
        rawResults = pool.map(task, tuple(task_arg_list))
        wins = [item for sublist in rawResults for item in sublist]


        avgWin = sum(wins) / len(wins)
        print(f"Win {avgWin} units per 100 hands on average")


#
# for i in range(1000):
#
#       profit = 0
#       for j in range(repetitions):
#             table2 = State(config2)
#             sB = table2.playerBankroll
#             start = time()
#             roundsPlayed = table2.play_rounds(iterations)
#             end = time()
#             eB = table2.playerBankroll
#
#
#             print(f"Done. Took {end-start} seconds for {roundsPlayed} rounds played."
#                   f"\n Final bankroll of {eB}, for a profit of {eB - sB}"
#                   f"\n Avg win per hand: {(eB-sB)/roundsPlayed}")
#
#             profit += eB - sB
#
#       outFile = open(f"Test_results/Test_results_bstrat{i}" , "w")
#       outFile.write(f"Profit after {iterations} rounds, played {repetitions} times using basic strategy: {profit}\n")
#       outFile.close()
#
#       profit = 0
#       for j in range(repetitions):
#             table1 = State(config1)
#             sB = table1.playerBankroll
#             start = time()
#             roundsPlayed = table1.play_rounds(iterations)
#             end = time()
#             eB = table1.playerBankroll
#
#
#             print(f"Done. Took {end-start} seconds for {roundsPlayed} rounds played."
#                   f"\n Final bankroll of {eB}, for a profit of {eB - sB}"
#                   f"\n Avg win per hand: {(eB-sB)/roundsPlayed}")
#
#             profit += eB - sB
#
#       outFile = open(f"Test_results/Test_results_counting{i}" , "w")
#       outFile.write(f"Profit after {iterations} rounds, played {repetitions} times using basic strategy: {profit}\n")
#       outFile.close()

# # Check files
# directory = os.listdir(r"Test_results")
#
# profitBst = 0
# winsBst = 0
# lossesBst = 0
# profitCount = 0
# winsCount = 0
# lossesCount = 0
# for entry in directory:
#      if entry < "Test_results_bt":
#            file = open(f"Test_results/{entry}", "r")
#            results = file.read().split(":")
#
#            profit = float(f"{results[1][:len(results[1])-2]}0")
#            if profit >= 0:
#                  winsBst += 1
#            else:
#                  lossesBst += 1
#
#            profitBst += profit
#      else:
#            file = open(f"Test_results/{entry}", "r")
#            results = file.read().split(":")
#
#            profit = float(f"{results[1][:len(results[1]) - 2]}0")
#            if profit >= 0:
#                  winsCount += 1
#            else:
#                  lossesCount += 1
#
#            profitCount += profit
#
# print(f"Each round of testing consists of {iterations * repetitions} hands of bj")
# print(f"Basic strategy wins: {winsBst}"
#       f"\nBasic strategy losses: {lossesBst}"
#       f"\nBasic strategy total profit after {iterations * repetitions * 2 * 280} hands: {profitBst}")
# print(f"Counting wins: {winsCount}"
#       f"\nCounting losses: {lossesCount}"
#       f"\nCounting total profit after {iterations * repetitions * 2 * 280} hands: {profitCount}")