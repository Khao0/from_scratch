import numpy as np

def softmax(xv):
    e_x = np.power(np.e, xv)
    return e_x/np.sum(e_x)


if __name__ =="__main__":
    result = softmax(np.array([0.8,0.2]))
    print(result)