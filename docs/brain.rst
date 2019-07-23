.. _brain:

Deep Learning
=======================================

   GEKKO specializes in a optimization and control. The **brain** module extends GEKKO with machine learning objects to facilitate the
   building, fitting, and validation of deep learning methods.

.. toctree::
	:maxdepth: 2


Deep Learning Properties
--------------

   GEKKO specializes in a unique subset of machine learning. However, 
   it can be used for various types of machine learning. This is a
   module to facilitate Artificial Neural Networks in GEKKO. Most ANN
   packages use gradient decent optimization. The solvers used in 
   GEKKO use more advanced techniques than gradient decent. 
   However, training neural networks may require extremely large 
   datasets. For these large problems, gradient decent does prove more
   useful because of the ability to massively parallelize. 
   Nevertheless, training in GEKKO is available for cases where the
   data set is of moderate size, for combined physics-based and 
   empirical modeling, or for other predictive modeling and 
   optimization applications that warrant a different solution strategy.

.. py:class::	b = brain.Brain(m=[],remote=True,bfgs=True,explicit=True):

	Creates a new `brain` object as a GEKKO model `m`. Option `remote`
   specifies if the problem is solved locally or remotely, `bfgs` uses
   only first derivative information with a BFGS update when `True`
   and otherwise uses first and second derivatives from automatic
   differentiation, `explicit` calculates the layers with 
   `Intermediate` equations instead of implicit `Equations`::
      
      from gekko import brain
      b = brain.Brain()
      
.. py:classmethod::    b.input_layer(size):

    Add an input layer to the artificial neural network. The input
    layer `size` is equal to the number of features or predictors that
    are inputs to the network.::
    
       from gekko import brain
       b = brain.Brain()
       b.input_layer(1)

.. py:classmethod::	  b.layer(linear=0,relu=0,tanh=0,gaussian=0,bent=0,leaky=0,ltype='dense'):

    Layer types: dense, convolution, pool (mean)
        
    Activation options: none, softmax, relu, tanh, sigmoid, linear::
    
       from gekko import brain
       b = brain.Brain()
       b.input_layer(1)
       b.layer(linear=2)
       b.layer(tanh=2)
       b.layer(linear=2)
       
    Each layer of the neural network may include one or multiple types
    of activation nodes. A typical network structure is to use a linear
    layer for the first internal and last internal layers with other
    activation functions in between.
    
.. py:classmethod::	  b.output_layer(size,ltype='dense',activation='linear'):

    Layer types: dense, convolution, pool (mean)
        
    Activation options: none, softmax, relu, tanh, sigmoid, linear::

       from gekko import brain
       b = brain.Brain()
       b.input_layer(1)
       b.layer(linear=2)
       b.layer(tanh=2)
       b.layer(linear=2)
       b.output_layer(1)

.. py:classmethod::	  b.learn(inputs,outputs,obj=2,gap=0,disp=True):

    Make the `brain` **learn** by adjusting the network weights to minimize
    the loss (objective) function. Give inputs as (n)xm, where n = input layer
    dimensions, m = number of datasets::

       from gekko import brain
       import numpy as np
       b = brain.Brain()
       b.input_layer(1)
       b.layer(linear=2)
       b.layer(tanh=2)
       b.layer(linear=2)
       b.output_layer(1)
       x = np.linspace(0,2*np.pi)
       y = np.sin(x)
       b.learn(x,y)

    Give outputs as (n)xm, where n = output layer dimensions, m = number of
    datasets. Objective can be 1 (l1 norm) or 2 (l2 norm). If obj=1, gap
    provides a deadband around output matching.

.. py:classmethod::	  b.shake(percent):

    Neural networks are non-convex. Some stochastic shaking can sometimes
    help bump the problem to a new region. This function perturbs all weights
    by +/-percent their values.

.. py:classmethod::	  b.think(inputs):

    Predict output based on `inputs`. The `think` method is used after the 
    network is trained. The trained parameter weights are used to calculates
    the new network outputs based on the input values.::
    
       from gekko import brain
       import numpy as np
       import matplotlib.pyplot as plt
       b = brain.Brain()
       b.input_layer(1)
       b.layer(linear=2)
       b.layer(tanh=2)
       b.layer(linear=2)
       b.output_layer(1)
       x = np.linspace(0,2*np.pi)
       y = np.sin(x)
       b.learn(x,y)
       xp = np.linspace(-2*np.pi,4*np.pi,100)
       yp = b.think(xp)
       plt.figure()
       plt.plot(x,y,'bo')
       plt.plot(xp,yp[0],'r-')
       plt.show()
       
       
