"""!
 @file progressivenessHelpers.py
 @author Owen Tanner Wilkerson (tanner.wilkerson@gmail.com)
 @brief Helper functions for the progressiveness mechanic
 @version 0.1
 @date 2021-01-30
 
 @copyright Copyright (c) 2021
 
"""
import discord
import redis
from discord.ext import commands
import json

from datetime import datetime
from dateutil import relativedelta
import pytz

import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import numpy as np
import pandas as pd
import math

def getAlphaAndBeta(t):
    """!
    @brief The the alpha and beta for the Beta Distribution at time t

    @param t The time 0.0-1.0 where 0 is the start of the campaign and 1.0 is the campaign climax
    """
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

class ProgHelp(commands.Cog):
    def __init__(self, bot, redisClient, dataHelp):
        self.bot = bot
        self.redisClient = redisClient
        self.dataHelp = dataHelp

    @commands.command(name='setT', help='Set the time and print out the growth lotus, the distribution, and alpha/beta values')
    async def setT(self, ctx, t):
        """!
        @brief This command get the name of the current campaign

        @param ctx Server context
        @param t Time (0.0 - 1.0 where 0.0 is the start of the campaign and 1.0 is the climax of the campaign)
        """
        t = float(t)
        self.redisClient.set('t', t)
        PlotGrowthCurve(t)
        GraphProgressivenessRoll(t)
        await ctx.send(file=discord.File('plotImage.png'))
        await ctx.send(file=discord.File('lotus.png'))
        await ctx.send(file=discord.File('lotusOverlay.png'))
        await ctx.send(file=discord.File('distribution.png'))
        alpha, beta = getAlphaAndBeta(t)
        response = "t = " + str(t) + " | alpha = " + str(alpha) + " | beta = " + str(beta)
        await ctx.send(response)

    @commands.command(name='getT', help='Print current T value and growth lotus')
    async def getT(self, ctx):
        """!
        @brief 

        @param ctx Server context
        """
        t = float(self.redisClient.get('t').decode("utf-8"))
        PlotGrowthCurve(t)
        await ctx.send(file=discord.File('lotusOverlay.png'))
        alpha, beta = getAlphaAndBeta(t)
        response = "t = " + str(t) + " | alpha = " + str(alpha) + " | beta = " + str(beta)
        await ctx.send(response)

    @commands.command(name='printDistribution', help='Print plot of current distribution')
    async def printDistribution(self, ctx):
        """!
        @brief 

        @param ctx Server context
        """

        t = float(self.redisClient.get('t').decode("utf-8"))
        GraphProgressivenessRoll(t)
        await ctx.send(file=discord.File('distribution.png'))
        response = "t = " + str(t)
        await ctx.send(response)

    @commands.command(name='rollProg', help='Roll Progressiveness')
    async def rollProg(self, ctx):
        """!
        @brief 

        @param ctx Server context
        """
        
        t = float(self.redisClient.get('t').decode("utf-8"))
        result = RollProgressiveness(t)
        response = str(result) + " - "
        if (result >= 1 and result <=5):
            response = response + "Very Counter-Progressive"
        elif (result >= 6 and result <=10):
            response = response + "Mildy Counter-Progressive"
        elif (result >= 11 and result <=15):
            response = response + "Mildly Progressive"
        elif (result >= 16 and result <=20):
            response = response + "Very Progressive"
        await self.dataHelp.incrementNumProgRolls();
        await ctx.send(response)

    @commands.command(name='rollAlign', help='Roll Alignment')
    async def rollAlign(self, ctx):
        """!
        @brief 

        @param ctx Server context
        """
        
        d20 = np.random.randint(1,20)
        response = str(d20) + " - "
        if (d20 >= 1 and d20 <=5):
            response = response + "Bad"
        elif (d20 >= 6 and d20 <=8):
            response = response + "Neutral leaning bad"
        elif (d20 >= 9 and d20 <=12):
            response = response + "True Neutral"
        elif (d20 >= 13 and d20 <=15):
            response = response + "Neutral leaning good"
        elif (d20 >= 16 and d20 <=20):
            response = response + "Good"
        await ctx.send(response)