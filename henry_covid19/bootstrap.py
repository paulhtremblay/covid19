import random
import numpy as np

def resample_two_samples(sample1, sample2, num_iterations = 100):
    assert isinstance(sample1, list) and isinstance(sample2, list)
    both = sample1 + sample2
    mean1 = []
    mean2 = []
    for i in range(num_iterations):
        random.shuffle(both) 
        new_1 = both[0:len(sample1)] 
        new_2 = both[len(sample1):] 
        mean1.append(np.mean(new_1)) 
        mean2.append(np.mean(new_2)) 
    return mean1, mean2

def combine_resamples(sample1, sample2, resample1, resample2):
    """
    combines the results of the resampling into an numpy array 
    that represents the differences between the sample means 
    and resample means.
    parameters:
       sample1: list of the original sample 1
       sample2: list of the original sample 2
       resample1: results of resampling sample 1
       resample2: result of resampling sample2
    returns:
        numpy array of the differences. the if loop makes sure that 
        the resulting array is always positive, so you can calculate the
        probability of the differences being > 0
    
    Example:
       sample1 is a sample in inches of students, [60, 59, 61.....]
       sample2 is a sample in inches of students, [72, 71, 70]
       resample1 is [63, 61, 60...]
       resamle2 is [63, 60, 59..]
       
       return [1, 2, 1, .5....]
       
       
    """
    diff1 = [np.mean(sample1 )- x for x in resample1]
    diff2 = [np.mean(sample2)- x for x in resample2]
    if np.mean(diff1) > np.mean(diff2):
        both = np.array(diff1) - np.array(diff2)
    elif np.mean(diff1) < np.mean(diff2):
        both = np.array(diff2) - np.array(diff1)
    else:
        #seriously? The same??
        both = np.array(diff2) - np.array(diff1)
    return both

def get_p_value(l, v = 0):
    """
    parameters:
      l list of floats or integers
    returns:
        float of the 1 - probability that  x > v
    """
    return  1 - len([x for x in l if x > v])/len(l)
    

