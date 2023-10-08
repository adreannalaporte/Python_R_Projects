""" Adreanna LaPorte
    ITP-449
    Final Project
    Linear Regression - Vehicle MPGs
"""


def main():
    # importing packages
    from sklearn.linear_model import LinearRegression
    import matplotlib.pyplot as plt
    import numpy as np
    import pandas as pd

    # reading in the csv
    file_path = 'auto-mpg.csv'
    df_mpgs = pd.read_csv(file_path)

    # steps 1 & 2: mean and median values for mpg
    df_described = df_mpgs.describe()
    print('Here are some descriptive statistics of the mpg data set:\n', df_described)
    mpg_mean = df_described.loc['mean', 'mpg']
    mpg_median = df_described.loc['50%', 'mpg']
    print(f'mpg mean: {mpg_mean}\nmpg median: {mpg_median}')

    # step 3: checking skewness based on mean and median
    if mpg_mean > mpg_median:
        print('\nmpg mean > mpg median --> this means that the data is right-skewed.')
    else:
        print('\nmpg mean < mpg median --> this means that the data is left-skewed.')
    plt.figure(1)
    plt.boxplot(df_mpgs['mpg'], vert=False)
    plt.title('MPG Boxplot to Display Skewness')
    plt.savefig('mpg_boxplot.png')

    # step 4: making the pairplot matrix
    # dropping 'No' & 'car_name'
    df_mpgs = df_mpgs.drop('No', axis=1)
    df_mpgs = df_mpgs.drop('car_name', axis=1)
    # creating pairwise plot
    dim = len(df_mpgs.columns)
    col_names = df_mpgs.columns
    fig, ax = plt.subplots(dim, dim, figsize=[32, 24])
    for i in range(dim):
        for j in range(dim):
            if i != j:
                ax[i, j].scatter(df_mpgs.iloc[:, i], df_mpgs.iloc[:, j])
            else:
                ax[i, j].hist(df_mpgs.iloc[:, i])
            if i == 0:
                ax[i, j].set_title(col_names[j])
            elif j == 0:
                ax[i, j].set_ylabel(col_names[i])

    fig.tight_layout()
    plt.savefig('pairplot_matrix.png')

    # step 5 & 6: using the pairplot to determine most strongly/weakly correlated attributes
    print('The most strongly correlated attributes appear to be mpg & displacement.')
    print('The most weakly correlated attributes appear to be displacement & model_year.')

    # step 7: scatterplot with displacement and mpg
    plt.figure(3)
    plt.scatter(df_mpgs['displacement'], df_mpgs['mpg'])
    plt.title('Displacement vs MPG: Scatterplot')
    plt.xlabel('Displacement')
    plt.ylabel('MPG')
    plt.savefig('scatterplot')

    # step 8: building a linear regression model
    x = df_mpgs['displacement']
    y = df_mpgs['mpg']

    model_linreg = LinearRegression()

    X = x.values.reshape(-1, 1)

    model_linreg.fit(X, y)

    y_pred = model_linreg.predict(X)
    residuals = y - y_pred

    # step 8, (1-5): printing slope vs intercept values, regression equation, predicted vals, etc.
    print('\nAnswers to questions for step 8:')
    print('1. b0:', model_linreg.intercept_)
    print('2. b1:', model_linreg.coef_)
    print(f'3. y = {model_linreg.intercept_} + {model_linreg.coef_}x')
    print('4. Based on the regression equation, as displacement increases, predicted value for mpg decreases.')
    df = pd.DataFrame({'displacement': [220]})
    specific_y_pred = model_linreg.predict(df.values)
    print(f'5. MPG prediction for a car with displacement of 220: {float(specific_y_pred)}')

    # step 8, 6: displaying a scatterplot with actual vals & regression equation
    plt.figure(4)
    plt.scatter(df_mpgs['displacement'], df_mpgs['mpg'])
    plt.plot(X, y_pred, color='r')
    plt.title('Displacement vs MPG: Scatterplot w/ Linear Regression Line')
    plt.xlabel('Displacement')
    plt.ylabel('MPG')
    plt.savefig('scatterplot_regressionline.png')

    # step 8, 7: plotting residuals
    fig, ax = plt.subplots(1, 2)
    ax[0].scatter(y_pred, residuals)
    ax[0].plot([y_pred.min(), y_pred.max()], [0, 0], color='red')
    ax[0].set(xlabel='Prediction', ylabel='Residuals', title='Residuals Plot')

    ax[1].hist(residuals, orientation='horizontal', bins=25)
    ax[1].set(xlabel='Distribution', title='Histogram')
    ax[1].yaxis.tick_right()
    fig.tight_layout()
    plt.savefig('residuals.png')


if __name__ == '__main__':
    main()
