## General

We consider a hierarchically-structured model of two CHPs using the block component in Pyomo. The CHPs are optimized against the electricity market. The cost function, consisting of gas costs and electricity revenues, is minimized.

The results are evaluated in the evaluation.ipynb.

## Chp class
The construction rule for the CHP blocks is handled as method of the Chp class in blocks/chp.py. On instantiation of the class, the base construction rule is provided. Further constraints can be added to the rule through kwargs (keyword arguments).