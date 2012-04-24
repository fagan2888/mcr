#!/usr/bin/env python
import numpy as np
from scipy.io import loadmat
from sklearn.cluster import KMeans
from sklearn.svm import NuSVR
from sklearn.metrics import mean_square_error
from sklearn.grid_search import GridSearchCV

from mcr import MIClusterRegress, Clusterer, RegressionModel

class KMeansClusterer(KMeans, Clusterer):
    """
    Implements a k-means clusterer for MIClusterRegress
    """
    def relevance(self, bag):
        """
        Relevance equal to one for closest bag and zero for others
        """
        dist = self.transform(bag).T
        closest = np.argmin(dist, axis=1)
        indicators = np.zeros(dist.shape)
        for row, c in enumerate(closest):
            indicators[row, c] = 1.0
        return Clusterer.normalize(indicators)

def regress():
    param_values = {
        'C': [10.0**i for i in (1, 2, 3, 4)],
        'nu': [0.2, 0.4, 0.4, 0.6],
        'kernel': ['linear'],
    }
    nu_svr = NuSVR(scale_C=True)
    grid_nu_svr = GridSearchCV(nu_svr, param_values,
        loss_func=mse, cv=5)
    return grid_nu_svr

def mse(y_hat, y):
    return np.average(np.square(y_hat - y))

def main():
    exset = loadmat('thrombin.mat', struct_as_record=False)['thrombin']

    # Construct bags
    all_labels = exset[:, 0]
    X = exset[:, 1:-1]
    bags = []
    values = []
    for label in np.unique(all_labels.flat):
        indices = np.nonzero(all_labels == label)
        bags.append(X[indices])
        values.append(float(exset[indices, -1][0, 0]))
    y = np.array(values)

    mcr = MIClusterRegress(KMeansClusterer(k=3), regress)
    mcr.fit(bags, y)
    y_hat = mcr.predict(bags)
    print 'MSE: %f' % mse(y_hat, y)

if __name__ == '__main__':
    main()
