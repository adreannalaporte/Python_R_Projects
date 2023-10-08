""" Adreanna
    ITP-449 Applications of Machine Learning
    Final Project
    Trees - Mushroom Edibility
"""


def main():
    # importing packages
    import pandas as pd
    import matplotlib.pyplot as plt
    from sklearn.model_selection import train_test_split
    from sklearn.tree import DecisionTreeClassifier, plot_tree
    from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay
    from sklearn.metrics import plot_confusion_matrix

    # displaying all rows and columns
    pd.set_option('display.width', None)
    pd.set_option('display.max_rows', None)

    # reading in the data
    file_path = 'mushrooms.csv'
    df_mushrooms = pd.read_csv(file_path)

    # separating features from target
    y = df_mushrooms['class']
    x = df_mushrooms.drop('class', axis=1)
    X = pd.get_dummies(x)

    # step 2: partition the dataset
    X_train, X_test, y_train, y_test = train_test_split(X, y, train_size=0.7, random_state=42, stratify=y)
    model_dt = DecisionTreeClassifier(criterion='entropy', random_state=42, max_depth=6)
    model_dt.fit(X_train, y_train)

    # step 4: confusion matrix (printed + visual)
    y_pred = model_dt.predict(X_test)
    conf_matrix = confusion_matrix(y_test, y_pred)
    print('Confusion matrix:\n', conf_matrix)
    plot_confusion_matrix(model_dt, X_test, y_test)
    plt.title('Confusion Matrix for Mushroom Classification')
    plt.tight_layout()
    plt.savefig('mushroom_confusion_matrix.png')

    # step 5: training accuracy score
    acc_score1 = model_dt.score(X_train, y_train)
    print('\ntrain accuracy score:', acc_score1)

    # step 6: test accuracy score
    acc_score2 = model_dt.score(X_test, y_test)
    print('\ntest accuracy score:', acc_score2)

    # step 7: plotting the tree
    plt.figure(2, figsize=(10, 8))
    plot_tree(model_dt, feature_names=X.columns, filled=True)
    plt.title('Decision Tree for Mushroom Classification')
    plt.tight_layout()
    plt.savefig('decision tree - mushroom.png')

    # step 8: top 3 most important features
    feat_import = model_dt.feature_importances_
    top_three = pd.Series(feat_import, index=X.columns).nlargest(3)
    print('\nTop 3 Most Important Features:')
    for feat in top_three.index:
        print(feat)

    # creating a dictionary with given features
    dictionary = {'cap-shape': 'x', 'cap-surface': 's', 'cap-color': 'n', 'bruises': 't', 'odor': 'y', 'gill-attachment': 'f',
    'gill-spacing': 'c', 'gill-size': 'n', 'gill-color': 'k', 'stalk-shape': 'e', 'stalk-root': 'e', 'stalk-surface-above-ring': 's',
    'stalk-surface-below-ring': 's', 'stalk-color-above-ring': 'w', 'stalk-color-below-ring': 'w', 'veil-type': 'p', 'veil-color': 'w',
    'ring-number': 'o', 'ring-type': 'p', 'spore-print-color': 'r', 'population': 's', 'habitat': 'u'}

    # converting to dataframe
    prediction_df = pd.DataFrame([dictionary])

    # combining categorical data with original feature data (appending as a row)
    combined_df = pd.concat([x, prediction_df], axis=0)
    new_df_dummies = pd.get_dummies(combined_df)

    # accessing last row that we just added and converting to dataframe & transposing
    pred_series = new_df_dummies.iloc[-1, :]
    pred_df = pd.DataFrame(pred_series).transpose()

    # step 9: making prediction for classification of mushroom
    prediction = model_dt.predict(pred_df)
    print('\nClassification of the mushroom: ', prediction[0])


if __name__ == '__main__':
    main()
