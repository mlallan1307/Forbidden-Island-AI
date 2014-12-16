"""
CS440 Assignment 3
Submitted by Michael Allan, CSUID 830484768
This program can be used to find MAX-SAT on given input files using multiple
local search strategies. It can also be used to run AStar to solve Huarong
Pass using heuristics.
"""

import search
import utils

import subprocess
import multiprocessing
import random
import copy
import math
import time
import sys
import os

OUTFILE = open('baseValuesResults.txt', 'w', 0)


#######################################
#             Classes
#######################################

class FORBIDDEN_ISLAND(search.Problem):
  def __init__(self, inFile):
    self.knownStates = {}
    self.stateCharges = {}
    with open(inFile, 'r') as fh:
      for line in fh:
        values = line.split(' : ')
        self.initial = [float(i) for i in values[0].split(', ')]
  
  def actions(self, state):
    """
    Returns a list with possible actions in the format given
    """
    rtn = []
    for i, baseValue in enumerate(state):
      rtn.append((i,  0.1))
      rtn.append((i, -0.1))
      rtn.append((i,  0.25))
      rtn.append((i, -0.25))
      rtn.append((i,  0.5))
      rtn.append((i, -0.5))
      rtn.append((i,  1.0))
      rtn.append((i, -1.0))
    return rtn


  def result(self, state, action):
    """
    Returns a state from the given action, state should be the tuple of tuples
    """
    tmp = list(state)
    tmp[action[0]] += action[1]
    return tmp


  def value(self, state):
    """
    Returns the value of the given state
    """
    strState = ','.join([str(v) for v in state])
    if strState in self.knownStates and (strState in self.stateCharges and \
        self.stateCharges[strState] > 0):
      print state, "known:", self.knownStates[strState], '%', self.stateCharges[strState]
      self.stateCharges[strState] -= 1
      return self.knownStates[strState]

    runs = 500
    wins = getValue(state, runs)

    rate =  float(wins)/runs*100
    print "Rate: {}/{} -> {}%".format(wins, runs, rate)
    print >> OUTFILE, "{} Rate: {}/{} -> {}%".format(state, wins, runs, rate)
    self.knownStates[strState] = rate
    self.stateCharges[strState] = 2 # 2 times without rechecking
    return rate


  def set_state(self, state):
      self.initial = state


class MaxTimeReached(Exception):
  pass

#######################################
#             Functions
#######################################


def getValue(state, runs):
  print state,
  q = multiprocessing.Manager().Queue()
  pool = multiprocessing.Pool(multiprocessing.cpu_count() + 1)

  jobs = []
  for i in range(runs):
    job = pool.apply_async(worker, (state, i, q))
    jobs.append(job)

  wins = 0
  fail = False
  for job in jobs:
    try:
      wins += getJob(job, pool, state, q)
    except Exception, e:
      print "Exception!", e
      fail = True
      break
    
  pool.close()

  if fail:
    pool.terminate()
    pool.join()
    print "Running again"
    return getValue(state, runs)

  pool.join()
  return wins


def getJob(job, pool, state, q):
  start = time.time()
  while True:
    if job.ready():
      break
    if time.time() - start > 15: # 15 second timeout
      raise Exception("Process took too long")
  return job.get()


def worker(state, run, q):
  p = subprocess.Popen(["python", "../forbidden_island.py", "a", "4", "0", "--baseValues",
                        '{}'.format(', '.join([str(v) for v in state])), "--load",
                        'savedStates.json', str(run)], 
                        stdout=subprocess.PIPE)
  out, err = p.communicate()
  return p.returncode

#______________________________________________________________________________
# Genetic Algorithm

def genetic_search(problem, fitness_fn, ngen=500, pmut=0.6, n=10):
  """Call genetic_algorithm on the appropriate parts of a problem.
  This requires the problem to have states that can mate and mutate,
  plus a value method that scores states."""
  states = [] # random pop
  for pop in range(n):
    problem.random_start()
    states.append(problem.initial)
  return genetic_algorithm(problem, states, problem.value, ngen, pmut)


def genetic_algorithm(problem, population, fitness_fn, ngen=1000, pmut=0.1):
  "[Fig. 4.8]"
  #MAX = 0
  for i in range(ngen):
    new_population = []
    '''
    print i, '------------'
    print '  ', MAX
    for p in population:
      print problem.value(p)
      if problem.value(p) > MAX:
        MAX = problem.value(p)
    '''
    for p in population:
      fitnesses = map(fitness_fn, population)
      s1, s2 = weighted_sample_with_replacement(population, fitnesses, 2)
      p1 = copy.copy(problem)
      p1.set_state(s1)
      p2 = copy.copy(problem)
      p2.set_state(s2)
      child = p1.mate(p2)
      child.mutate(pmut)
      new_population.append(child.initial)
    population = new_population
  return utils.argmax(population, fitness_fn)


def weighted_sample_with_replacement(seq, weights, n):
  """Pick n samples from seq at random, with replacement, with the
  probability of each element in proportion to its corresponding
  weight."""
  myWeights, mySeq = zip(*sorted(zip(weights, seq)))
  return [weighted_sampler(mySeq, myWeights) for s in range(n)]


def weighted_sampler(seq, weights):
  "Return a random-sample function that picks from seq weighted by weights."
  biasedWeights = list(weights)
  for idx, w in enumerate(weights):
    biasedWeights[idx] = ((idx+1)/float(len(weights)))**(math.log(0.5)/math.log(0.9))
  minFit = random.random()
  return seq[random.choice([idx for idx, x in enumerate(biasedWeights) if x>=minFit])]


def annealing_schedule(k=5, lam=0.005, limit=10000):
    "One possible schedule function for simulated annealing"
    return lambda t: utils.if_(t < limit, k * math.exp(-lam * t), 0)


def run_local_search(runType, inFile, outFile=OUTFILE):
  print >> outFile, '--------------------------------'
  fi = FORBIDDEN_ISLAND(inFile)
  if runType == 'SA':
    print >> outFile, 'Simulated Annealing'
    sTime = time.time()
    rtn = search.simulated_annealing(fi, annealing_schedule())
    print >> outFile, '  Time: {} secs'.format(time.time()-sTime)
    print >> outFile, '  Value: {}'.format(fi.value(rtn.state))
    print >> outFile, '  baseValues: {}'.format(rtn.state)
  elif runType == 'GA':
    print >> outFile, 'Genetic Algorithm'
    sTime = time.time()
    rtn = genetic_search(fi, fi.value)
    print >> outFile, '  Time: {} secs'.format(time.time()-sTime)
    print >> outFile, '  Value: {} / {}'.format(fi.value(rtn),  fi.numClause)
  elif runType == 'StA':
    print >> outFile, 'Steepest ascent'
    sTime = time.time()
    rtn = search.hill_climbing(fi)
    print >> outFile, '  Time: {} secs'.format(time.time()-sTime)
    print >> outFile, '  Value: {} / {}'.format(fi.value(rtn),  fi.numClause)
  elif runType == 'StAR':
    print >> outFile, 'Steepest ascent random restarts'
    valueL = []
    timeL = []
    for r in range(20):
      sTime = time.time()
      fi.random_start()
      rtn = search.hill_climbing(fi)
      timeL.append(time.time()-sTime)
      valueL.append(fi.value(rtn))
    print >> outFile, '  Time: {} secs'.format(sum(timeL)/float(len(timeL)))
    print >> outFile, '  Mean: {} / {}'.format(sum(valueL)/float(len(valueL)),  fi.numClause)
    print >> outFile, '  Min: {} / {}'.format(min(valueL),  fi.numClause)
    print >> outFile, '  Max: {} / {}'.format(max(valueL),  fi.numClause)


#######################################
#               Main
#######################################

if __name__ == "__main__":
  run_local_search('SA', 'baseValues.txt')
  #run_maxsat()
  #run_huarong_pass_BFS()
  #run_huarong_pass()

