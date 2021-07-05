# -*- coding: utf-8 -*-
"""
Created on Fri Apr 10 20:46:55 2020
@author: FSalinas
email: fabio.salinas1982@gmail.com
"""

def getstats(X, varname, graphtitle = '', fontsize = 30, figsize = (17,7)):
    '''
    Plot a histogram, a density plot and a boxplot for a numeric variable
    
    Parameters
    ----------
    X : LIST with numeric values
    varname : STRING with the name of the variable
    graphtitle : Chart title
    fontsize : Size for the text chart title
    figsize : Size for the complete chart
    
    Returns two objects: outliers, ndf
    -------
    outliers: List with the outlier values.
    ndf: Dictionary with trhe statistic values calculated.
    f: the figure of the chart
    
    Use examples:
    X1 = [1,5,3,74,52,8,2,8,2,85,2,5,5,2,2,16,185,62,2]
    X2 = [1,2,3,4,5,6,1,2,3,4,5,6]
    varname1 = 'test1'
    varname2 = 'test2'
    o1, s1, g1 = getstats(X1, varname1, graphtitle = 'Chart No 1', fontsize = 20, figsize = (10,5))
    o2, s2, g2 = getstats(X2, varname2, graphtitle = 'Second Chart', fontsize = 30, figsize = (17,7))
    '''
    import matplotlib.pyplot as plt
    from matplotlib.cbook import boxplot_stats
    import pandas as pd
    import seaborn as sns
    import numpy as np
    from scipy import stats
    plt.style.use('seaborn-whitegrid')
    # sns.set_palette("deep", desat=.6)
    
    f, (ax_box, ax_hist) = plt.subplots(
        2,
        sharex = True,
        figsize = figsize if figsize[1] > 5 else (figsize[0], 6),
        gridspec_kw = {"height_ratios": (0.2, 1)}
    )
    
    outliers = [y for stat in boxplot_stats(X) for y in stat['fliers']]
    
    description = pd.DataFrame(
        X,
        columns=[varname]
    ).describe()
    ndf = {}
    for med in description.index:
        ndf[med] = round(description.loc[med][0], 2)
    ndf['median'] = round(np.median(X), 2)
    ndf['mode'] = round(list(stats.mode(X))[0][0], 2)
    ndf['kurtosis'] = round(stats.kurtosis(X), 2)
    ndf['skewness'] = round(stats.skew(X), 2)
    ndf['# outliers'] = len(outliers)
    print(str(ndf))
    sdf = pd.DataFrame(data=None, columns = ['variable', 'value'])
    sdf['variable'] = list(ndf.keys())
    sdf['value'] = list(ndf.values())

    sns.boxplot(X, ax = ax_box).set_title(graphtitle, fontsize = fontsize)
    ax_box.axvline(ndf['mean'], color = 'r', linestyle = '--')
    ax_box.axvline(ndf['median'], color = 'g', linestyle = '-')
	
    sns.distplot(X, ax = ax_hist)
    ax_hist.axvline(ndf['mean'], color = 'r', linestyle = '--')
    ax_hist.axvline(ndf['median'], color = 'g', linestyle = '-')

    plt.legend({'Media':ndf['mean'],'Mediana':ndf['median']})
    ax_hist.set(xlabel=varname)
    
    sl = []
    for fil in sdf.index:
        sl += ['{var}: {val:,.2f}'.format(var = sdf.loc[fil,'variable'], val = sdf.loc[fil,'value'])]

    textstr = '\n'.join(sl)

    props = dict(boxstyle='round', facecolor='#eafff5', alpha=0.5)

    ax_hist.text(
        0.05,
        0.95,
        textstr,
        transform = ax_hist.transAxes,
        fontsize = 14,
        verticalalignment = 'top',
        bbox = props
    )

    return(outliers, ndf, f)