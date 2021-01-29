from datetime import datetime
from dateutil import relativedelta
import pytz

import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import numpy as np
import pandas as pd
import math

def getAlphaAndBeta(t):
    maxY = 1
    a3 = maxY/np.power(0.5,3)
    a2 = maxY/np.power(0.5,2)
    a15 = maxY/np.power(0.5,1.5)
    a1 = maxY/np.power(0.5,1)

    if (t < 0.5):
        return 1, a1*np.abs(t-0.5)+1
    else:
        return (a3*np.power(np.abs(t-0.5), 3) + a2*np.power(np.abs(t-0.5), 2) + a2*np.power(np.abs(t-0.5), 2) + a15*np.power(np.abs(t-0.5), 1.5))/4.0 + 1, 1

def GraphProgressivenessRoll(t):
    # Generate the distribution of a twenty-sided dice

    # alpha_range_d20 = [1, 2];
    # beta_range_d20 = [2, 1];
    # alpha_d20 = 1.2
    # beta_d20 = 1.2
    alpha_d20, beta_d20 = getAlphaAndBeta(t);
    skew_d20 = np.random.beta(alpha_d20, beta_d20, 1000000);
    skew_d20 = (np.round(skew_d20, 3)*19)+1

    plt.hist(skew_d20, density=True, bins=20, rwidth=0.5);
    plt.ylabel('Probability')
    plt.xlabel('Roll')
    plt.savefig("distribution.png")
    plt.clf()

def RollProgressiveness(t):
    # Generate the distribution of a twenty-sided dice

    # alpha_range_d20 = [1, 2];
    # beta_range_d20 = [2, 1];
    #alpha_d20 = 1.4
    #beta_d20 = 1
    alpha_d20, beta_d20 = getAlphaAndBeta(t);
    skew_d20 = np.random.beta(alpha_d20, beta_d20);
    skew_d20 = (np.round(skew_d20, 3)*19)+1

    #IncrementNumProgressRolls()

    #print(np.round(skew_d20))
    return np.round(skew_d20)

def PlotGrowthCurve(tGuess):

    t = np.arange(0,1,0.0001)

    maxY = 1
    a4 = maxY/np.power(0.5,4)
    a3 = maxY/np.power(0.5,3)
    a2 = maxY/np.power(0.5,2)
    a15 = maxY/np.power(0.5,1.5)
    a1 = maxY/np.power(0.5,1)

    print("Linear: ", a1*np.abs(tGuess-0.5)+1)
    print("Dampened Quadratic: ", (a3*np.power(np.abs(tGuess-0.5), 3) + a2*np.power(np.abs(tGuess-0.5), 2) + a2*np.power(np.abs(tGuess-0.5), 2) + a15*np.power(np.abs(tGuess-0.5), 1.5))/4.0 + 1)
    print("Quartic: ", a4*np.power(np.abs(tGuess-0.5), 4)+1)

    curve = (a3*np.power(np.abs(t-0.5), 3) + a2*np.power(np.abs(t-0.5), 2) + a2*np.power(np.abs(t-0.5), 2) + a15*np.power(np.abs(t-0.5), 1.5))/4.0 + 1
    curve1 = a1*np.abs(t-0.5)+1
    curve2 = a4*np.power(np.abs(t-0.5), 4)+1

    plt.plot(t, curve)
    plt.plot(t, curve1)
    plt.plot(t, curve2)
    plt.axvline(x=tGuess)
    plt.xlabel('t')
    plt.ylabel('S(t)')

    plt.savefig("lotus.png")

    plt.clf()

    img = mpimg.imread('plotImage.png')
    height, width, _ = img.shape
    t = np.arange(-250,250,0.0001)

    maxY = height/2
    a4 = maxY/np.power(250,4)
    a3 = maxY/np.power(250,3)
    a2 = maxY/np.power(250,2)
    a15 = maxY/np.power(250,1.5)
    a1 = maxY/np.power(250,1)

    curve = -(a3*np.power(np.abs(t), 3) + a2*np.power(np.abs(t), 2) + a2*np.power(np.abs(t), 2) + a15*np.power(np.abs(t), 1.5))/4.0 + height*(4/6)
    curve1 = -a1*np.abs(t)+height*(4/6)
    curve2 = -a4*np.power(np.abs(t), 4)+height*(4/6)

    tPlot = np.arange(25,525,0.0001)
    implot = plt.imshow(img)
    plt.plot(tPlot, curve)
    plt.plot(tPlot, curve1)
    plt.plot(tPlot, curve2)
    plt.axvline(x=25+500*tGuess)
    plt.xlabel('t')
    plt.ylabel('S(t)')
    plt.savefig("lotusOverlay.png")
    plt.clf()