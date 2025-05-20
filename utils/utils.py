import numpy as np

def softmax(xv):
    e_x = np.power(np.e, xv-np.max(xv)) # subtract for preventing from high computation of exponent high value
    return e_x/np.sum(e_x)

def sigmoid(xv):
    return 1/(1+np.exp(-xv))


if __name__ =="__main__":
    result = sigmoid(np.array([0.8,0.2]))
    print(result)