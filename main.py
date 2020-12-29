import os
from libs.playBj import State
from yaml import load, FullLoader
from time import time

cfg1 = open("libs/ConfigureBJ.yaml", 'r')
cfg2 = open("libs/Basic_Strategy.yaml", 'r')
cfg3 = open("libs/Profbj_benchmark.yaml", 'r')
config1 = load(cfg1, Loader=FullLoader)
config2 = load(cfg2, Loader=FullLoader)
config3 = load(cfg3, Loader=FullLoader)

handNum = 100000
iterations = 6000
wins = []

#Need to find winrate per 100 hands
bankruptCount = 0

for i in range(iterations):
    print(i)
    try:
        table = State(config3)

        start = table.playerBankroll
        bankruptAt = table.play_rounds(handNum)
        end = table.playerBankroll

        wins.append(end-start)
    except KeyboardInterrupt:
        print("Ending sim early due to Keyboard Interrupt")
        iterations = i
        break
print(f"Average win per {handNum} hands after {iterations} iterations: ${10 * (sum(wins)/len(wins))}")
print(f"Wins list ({len(wins)} entries): {wins}")


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