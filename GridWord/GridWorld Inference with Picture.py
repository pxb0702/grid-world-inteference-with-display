import numpy as np
import tensorflow as tf
import gym
import random
import itertools
import scipy.misc
import matplotlib.pyplot as plt
import os
import time
import pygame
# import PIL 

##########################################################
###  start to creat the object class
###  the parameters for this class : 
###     - Coordinators  :  x, y, where to put the picture
###     - Size          :  the size of the object
###     - intensity     :  how bright / which color
###     - Channel       :  the color of the block
###     - Reward        :  reward after each step
###     - Name          :  the name of the object to create
#########################################################
class gameOb() : 
    def __init__(self, coordinators, size, intensity, channel, reward, name) : 
        self.x = coordinators[0]
        self.y = coordinators[1]
        self.size = size
        self.intensity = intensity
        self.channel = channel
        self.reward = reward
        self.name = name

class gameEnv() : 
    def __init__(self, size) : 
        self.sizeX = size
        self.sizeY = size
        self.actions = 4
        self.windowWdith = 700
        self.windowHeight = 700
        self.width_margin = self.windowWdith // 7
        self.height_margin = self.windowHeight //7
        self.block_width = self.width_margin
        self.block_height = self.height_margin
        self.bg_color = (128,128,128)
        self.hero_color = (0,0,255)
        self.fire_color = (255,0,0)
        self.goal_color = (0,255,0)
        pygame.init()
        self.screen = pygame.display.set_mode((self.windowWdith,self.windowHeight))
        pygame.display.set_caption("Grid World display - programming running")
        self.screen.fill(self.bg_color)
        self.objects = []
        a = self.reset()
        self.drawEnv()
        # plt.imshow(a, interpolation='nearest')
        # plt.show()

    def drawEnv(self) : 

        pygame.draw.rect(self.screen, (0,0,0),  (self.width_margin,self.height_margin,
                        self.windowWdith-2*self.width_margin, 
                        self.windowHeight-2*self.height_margin))
        for item in self.objects : 
            if item.name == 'hero' : 
                pygame.draw.rect(self.screen, self.hero_color,  
                        (self.width_margin + item.x * self.block_width,
                        self.height_margin + item.y * self.block_height,
                        self.block_width,self.block_height))
            if item.name == 'goal' : 
                pygame.draw.rect(self.screen, self.goal_color,  
                        (self.width_margin + item.x * self.block_width,
                        self.height_margin + item.y * self.block_height,
                        self.block_width,self.block_height))
            if item.name == 'fire' : 
                pygame.draw.rect(self.screen, self.fire_color,  
                        (self.width_margin + item.x * self.block_width,
                        self.height_margin + item.y * self.block_height,
                        self.block_width,self.block_height))
        pygame.display.update()

        return
    
    def reset(self) : 
        self.objects = []
        hero = gameOb(self.newPosition(), 1,1,2, None, 'hero')
        self.objects.append(hero)
        goal_00 = gameOb(self.newPosition(), 1,1,1,1, 'goal')
        self.objects.append(goal_00)
        fire_00 = gameOb(self.newPosition(), 1,1,0,-1, 'fire')
        self.objects.append(fire_00)
        goal_01 = gameOb(self.newPosition(), 1,1,1,1, 'goal')
        self.objects.append(goal_01)
        fire_01 = gameOb(self.newPosition(), 1,1,0,-1, 'fire')
        self.objects.append(fire_01)
        goal_02 = gameOb(self.newPosition(), 1,1,1,1, 'goal')
        self.objects.append(goal_02)
        goal_03 = gameOb(self.newPosition(), 1,1,1, 1, 'goal')
        self.objects.append(goal_03)
        state = self.renderEnv()
        self.state = state
        return state

    ##########################################################
    ###  moveChar function:  to move the char according to direction
    ###  Direction :  
    ###     - 0  :  up
    ###     - 1  :  down
    ###     - 2  :  left
    ###     - 3  :  right
    #########################################################
    def moveChar(self, direction) : 
        hero = self.objects[0]
        heroX = hero.x
        heroY = hero.y
        if direction == 0 and hero.y >= 1 : 
            hero.y -= 1
        if direction == 1 and hero.y <=self.sizeY-2 : 
            hero.y += 1
        if direction == 2 and hero.x >= 1 : 
            hero.x -= 1
        if direction == 3 and hero.x <= self.sizeX - 2 : 
            hero.x += 1
        self.objects[0]= hero

    ##########################################################
    ###  newPosition : return a random free space
    #########################################################
    def newPosition(self) : 
        iterables =[range(self.sizeX), range(self.sizeY)]
        points = []
        for t in itertools.product(*iterables) : 
            points.append(t)
        currentPositions = []
        for objectA in self.objects : 
            if (objectA.x, objectA.y) not in currentPositions : 
                currentPositions.append((objectA.x, objectA.y))
        for pos in currentPositions : 
            points.remove(pos)
        location = np.random.choice(range(len(points)), replace = False)
        return points[location]

    ##########################################################
    ###  CheckGoal : to check if 'hero' contact any of the objects
    #########################################################
    def checkGoal (self) : 
        others = []
        for obj in self.objects : 
            if obj.name == 'hero' : 
                hero = obj 
            else : 
                others.append(obj)
        for other in others : 
            if hero.x == other.x and hero.y == other.y : 
                self.objects.remove(other)
                if other.reward == 1 : 
                    self.objects.append(gameOb(self.newPosition(), 1, 1, 1,1,'goal'))
                else : 
                    self.objects.append(gameOb(self.newPosition(), 1, 1, 0,-1,'fire'))
                return other.reward, False 
        return 0.0, False 

    def renderEnv(self) : 
        a = np.ones([self.sizeX +2, self.sizeY+2, 3]) 
        a[1:-1, 1:-1, :] = 0  # what doesn' this mean ? 
        hero = None
        for item in self.objects : 
            a[item.y+1 : item.y+item.size+1, item.x+1 : item.x + item.size + 1, 
                item.channel] = item.intensity
        b = scipy.misc.imresize(a[:,:,0], [84,84,1],interp='nearest')
        c = scipy.misc.imresize(a[:,:,1], [84,84,1],interp='nearest')
        d = scipy.misc.imresize(a[:,:,2], [84,84,1],interp='nearest')
        a = np.stack([b,c,d], axis = 2)
        return a

    def step(self, action) : 
        self.moveChar(action)
        reward, done = self.checkGoal()
        state = self.renderEnv()
        return state, reward, done

env = gameEnv(size = 5)

class Qnetwork() : 
    def __init__(self, h_size) :
        self.scalarInput = tf.placeholder(shape = [None, 21168], dtype = tf.float32)
        self.imageIn = tf.reshape(self.scalarInput, [-1, 84, 84, 3])
        self.conv1 = tf.contrib.layers.convolution2d (
            inputs = self.imageIn, num_outputs = 32, 
            kernel_size = [8,8], stride = [4,4], 
            padding = 'VALID', biases_initializer = None) 
        self.conv2 = tf.contrib.layers.convolution2d(
            inputs = self.conv1, num_outputs = 64, kernel_size = [4,4], 
            stride = [2,2], padding = 'VALID', biases_initializer = None)
        self.conv3 = tf.contrib.layers.convolution2d(
            inputs = self.conv2, num_outputs = 64, kernel_size = [3,3], 
            stride = [1,1], padding = 'VALID', biases_initializer = None)
        self.conv4 = tf.contrib.layers.convolution2d(
            inputs = self.conv3, num_outputs = 512, kernel_size = [7,7], 
            stride = [1,1], padding = 'VALID', biases_initializer = None)
        self.streamAC, self.streamVC = tf.split(self.conv4, 2, 3)
        self.streamA = tf.contrib.layers.flatten(self.streamAC)
        self.streamC = tf.contrib.layers.flatten(self.streamVC)
        # here, the h_size must be 512, or the parameters will not matching, we can change 512 -> h_size
        self.AW = tf.Variable(tf.random_normal([h_size//2, env.actions]))
        self.VW = tf.Variable(tf.random_normal([h_size//2, 1]))

        self.Advantage = tf.matmul(self.streamA, self.AW)
        self.Value = tf.matmul(self.streamC, self.VW)

        self.Qout = self.Value + tf.subtract(self.Advantage, tf.reduce_mean(
                    self.Advantage, reduction_indices=1, keepdims=True ))
        self.predict = tf.argmax(self.Qout, 1)

        self.targetQ = tf.placeholder(shape = [None], dtype = tf.float32)
        self.actions = tf.placeholder(shape = [None], dtype = tf.int32)
        self.actions_onehot = tf.one_hot(self.actions, env.actions, dtype=tf.float32)
        self.Q = tf.reduce_sum(tf.multiply(self.Qout, self.actions_onehot), 
                    reduction_indices=1)
        self.td_error = tf.square(self.targetQ -self.Q)
        self.loss = tf.reduce_mean(self.td_error)
        self.trainer = tf.train.AdamOptimizer(learning_rate=0.0001)
        self.updateModel = self.trainer.minimize(self.loss)

class experience_buffer() : 
    def __init__(self, buffer_size = 50000) : 
        self.buffer = []
        self.buffer_size = buffer_size

    def add(self, expereince) : 
        if(len(self.buffer) + len(expereince) >= self.buffer_size) : 
            self.buffer[0:(len(self.buffer) + len(expereince))- self.buffer_size] = []
        self.buffer.extend(expereince)
    
    def sample(self, size) : 
        return np.reshape(np.array(random.sample(self.buffer, size)), [size, 5])

def processState(states) : 
    return np.reshape(states, [21168])

def updateTargetGraph (tfVars, tau) : 
    total_vars = len(tfVars)
    op_holder = []
    for idx, var in enumerate(tfVars[0:total_vars//2]) : 
        op_holder.append(tfVars[idx + total_vars//2].assign((var.value()*\
                        tau)+ ((1-tau)*tfVars[idx+total_vars//2].value())))
    return op_holder

def updateTarget (op_holder, sess): 
    for op in op_holder : 
        sess.run(op)

batch_size = 32
update_freq = 4
y = 0.99
startE = 1
endE = 0.1
anneling_steps = 10000
# num_espisodes = 10000
num_espisodes = 100
pre_train_steps = 10000
max_epLength = 50
load_model = True
path = './dqn_saved_Feb_26'
h_size = 512
tau = 0.001

# create two QN networks, one for Main, one for TargetQN. 
mainQN = Qnetwork(h_size)
targetQN = Qnetwork(h_size)
init = tf.global_variables_initializer()

trainables = tf.trainable_variables()
targetOps = updateTargetGraph(trainables, tau)

myBuffer = experience_buffer()

e=startE
stepDrop = (startE - endE) / anneling_steps

rList = []
total_steps = 0

saver = tf.train.Saver()
if not os.path.exists(path) : 
    os.mkdir(path)


with tf.Session() as sess : 
    # pygame.init()
#    screen = pygame.display.set_mode((400, 300))
#    pygame.display.set_caption(" Grid World ")
#    screen.fill((0,0,0))
    if load_model == True : 
        print('loading models ......')
        ckpt = tf.train.get_checkpoint_state(path)
        saver.restore(sess, ckpt.model_checkpoint_path)
#    sess.run(init)
#    updateTarget(targetOps, sess)
#region Code by Leyan
#    plt.ion()
#endregion Code by Leyan
    for i in range(num_espisodes + 1) : 
        episodeBuffer = experience_buffer()
        s = env.reset()
        s = processState(s)
        d = False
        rAll = 0
        j = 0
        start_time = time.time()
        
        while j < max_epLength : 
            j += 1
#            if np.random.rand(1) < e or total_steps < pre_train_steps : 
#                a = np.random.randint(0,4)
#            else : 
            a = sess.run(mainQN.predict, feed_dict={mainQN.scalarInput:[s]})[0]
            s1, r, d = env.step(a)
#region Code by Leyan
#            plt.imshow(s1, interpolation='nearest')
#            plt.pause(0.2)
#endregion Code by Leyan
            env.drawEnv()
            s1 = processState(s1)
            total_steps += 1
            time.sleep(0.5)
#            episodeBuffer.add(np.reshape(np.array([s,a,r,s1,d]),[1,5]))
#            if total_steps > pre_train_steps : 
#                if e > endE : 
#                    e -= stepDrop
#                if total_steps % (update_freq) == 0 :
#                    trainBatch = myBuffer.sample(batch_size)
#                    A = sess.run(mainQN.predict, feed_dict = {
#                        mainQN.scalarInput:np.vstack(trainBatch[:,3])})
#                    Q = sess.run(targetQN.Qout, feed_dict = {
#                        targetQN.scalarInput:np.vstack(trainBatch[:,3])})
#                    doubleQ = Q[range(batch_size), A]
#                    targetQ = trainBatch[:,2] + y*doubleQ
#                    _ = sess.run(mainQN.updateModel, feed_dict = {
#                        mainQN.scalarInput:np.vstack(trainBatch[:,0]),
#                        mainQN.targetQ:targetQ,
#                        mainQN.actions:trainBatch[:,1]})
#                    
#                    updateTarget(targetOps, sess)
            rAll += r
            s = s1

            if d == True : 
                break
        time_used = time.time() - start_time
        print('Episode : %d , Reward :  %d,  use time : %f '%(i, rAll, time_used))

#        myBuffer.add(episodeBuffer.buffer)
#        rList.append(rAll)
#        if i>0 and i%25 == 0: 
#            print('episode  ', i, '  , average reward of last 25 episides', 
#                np.mean(rList[-25:]))
#            if i > 0 and i%1000 == 0 : 
#                saver.save(sess, path + '/model -' + str(i) + '.cptk')
#                print("Saved Model")
    
#    saver.save(sess, path + '/model -' + str(i) + '.cptk')

'''
rMat = np.resize(np.array(rList),[len(rList)//100, 100])
rMean = np.average(rMat,1)
plt.plot(rMean)
'''

'''
while (1) : 
    print('succussfully run the program')
    time.sleep(5)

'''





        



          
