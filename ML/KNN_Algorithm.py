""" Adreanna LaPorte
    ITP-449 
    Applications of Machine Learning
    Final Project
    KNN - Wine Quality Classification
"""


def main():
    # importing packages:
    import pandas as pd
    import matplotlib.pyplot as plt
    from sklearn.preprocessing import Normalizer
    from sklearn.model_selection import train_test_split
    from sklearn.neighbors import KNeighborsClassifier
    from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay

    # step 1: reading in data
    pd.set_option('display.width', None)
    pd.set_option('display.max_columns', None)
    file_path = 'winequality.csv'
    df_wines = pd.read_csv(file_path)

    # step 2: standardize all variables except quality
    y = df_wines['Quality']
    x = df_wines.drop(['Quality'], axis=1)
    norm = Normalizer()
    X = pd.DataFrame(norm.fit_transform(x), columns=x.columns)

    # step 3: partitioning dataset with test and validation
    X_train, X_temp, y_train, y_temp = train_test_split(X, y, random_state=42, train_size=0.6, stratify=y)
    X_valid, X_test, y_valid, y_test = train_test_split(X_temp, y_temp, random_state=42, train_size=0.5, stratify=y_temp)


    # step 4: iterate on different ks (1 to 30), train, predict, gather accuracies
    # step 5: building KNN model to predict quality
    ks = range(1, 31)
    t_scores = []
    v_scores = []
    for k in ks:
        # import and instantiate algorithm
        model_knn = KNeighborsClassifier(n_neighbors=k)
        model_knn.fit(X_train, y_train)
        training_score = model_knn.score(X_train, y_train)
        t_scores.append(training_score)
        validation_score = model_knn.score(X_valid, y_valid)
        v_scores.append(validation_score)

    # step 6: plotting the accuracy for training and validations
    fig, ax = plt.subplots(1, 2)
    ax[0].plot(ks, t_scores)
    ax[0].set(xlabel='K neighbors', ylabel='Training Accuracy Score')
    ax[0].set_title('Training Accuracy for various k\'s', size=10)
    ax[1].plot(ks, v_scores)
    ax[1].set(xlabel='K neighbors', ylabel='Validation Accuracy Score')
    ax[1].set_title('Validation Accuracy for various k\'s', size=10)
    plt.tight_layout()
    plt.savefig('knn_accuracyscores.png')

    # step 7: best k value
    print('For both training and validation, k = 1 produced the best accuracy.')

    # step 8: generating predictions for test partition & plot confusion matrix
    model_knn = KNeighborsClassifier(n_neighbors=1)
    model_knn.fit(X_test, y_test)
    y_pred = model_knn.predict(X_test)

    conf_matrix = confusion_matrix(y_test, y_pred)
    cm_disp = ConfusionMatrixDisplay(confusion_matrix=conf_matrix, display_labels=model_knn.classes_)
    fig, ax1 = plt.subplots()
    cm_disp.plot(ax=ax1)
    plt.title('Confusion Matrix for Wine Quality Classification')
    plt.tight_layout()
    plt.savefig('confusion_matrix.png')

    # step 9: printing accuracy of model on the test dataset
    acc_score = model_knn.score(X_test, y_pred)
    print('accuracy score (test dataset):', acc_score)

    # step 10: printing the test df w Quality and Predicted Quality
    qual_dict = {'Quality': y_test, 'Predicted Quality': y_pred}
    df_pred_qual = pd.DataFrame(qual_dict)

    print_df = pd.concat([X_test, df_pred_qual], axis=1, join='inner')
    print('\n\nCombined DataFrame:\n', print_df)


if __name__ == '__main__':
    main()
