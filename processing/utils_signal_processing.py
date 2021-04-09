import numpy as np


def clean_outliers(templates, way = 'q'):

    var = templates.var(axis=1)

    if way == 'q':
        q3 = np.quantile(var, 0.75)
        q1 = np.quantile(var, 0.25)
        iqr = q3 - q1
        templates = templates[~((var < (q1 - 1.5 * iqr)) |(var > (q3 + 1.5 * iqr)))]

   # elif way == 'z':
    #    new_features = features[(zscore(features) < 3).all(axis=1)]

    #print(len(features)-len(new_features), ' points removed')

    return templates



def normalise_feats(features, norm='minmax'):

    if norm == 'stand':
        norm_features = (features - features.mean())/(features.std())

    elif norm == 'minmax':
        norm_features = (features - features.min())/(features.max()-features.min())

    return norm_features
