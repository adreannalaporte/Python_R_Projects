""" Adreanna LaPorte
    ITP-449
    Final Project
    Trees - Personal Loan Prediction
"""


def main():
    import pandas as pd
    import matplotlib.pyplot as plt
    from sklearn.model_selection import train_test_split
    from sklearn.tree import DecisionTreeClassifier, plot_tree
    from sklearn.metrics import confusion_matrix, classification_report, ConfusionMatrixDisplay

    file_path = 'UniversalBank.csv'
    df_bank = pd.read_csv(file_path)

    # step 1: establishing target variable
    print('Target Variable = Personal Loan')

    # step 2: removing unnecessary attributes
    df_bank = df_bank.drop('Row', axis=1)
    df_bank = df_bank.drop('ZIP Code', axis=1)

    y = df_bank['Personal Loan']
    X = df_bank.drop('Personal Loan', axis=1)

    # step 3/6: partition the dataset & creating the tree
    X_train, X_test, y_train, y_test = train_test_split(X, y, train_size=0.7, random_state=42, stratify=y)
    model_dt = DecisionTreeClassifier(criterion='entropy', random_state=42, max_depth=5)
    model_dt.fit(X_train, y_train)

    # step 5: confusion matrix to show answers for questions on training partition
    y_pred = model_dt.predict(X_train)
    conf_matrix = confusion_matrix(y_train, y_pred)
    cm_disp = ConfusionMatrixDisplay(confusion_matrix=conf_matrix, display_labels=model_dt.classes_)
    fig, ax1 = plt.subplots()
    cm_disp.plot(ax=ax1)
    plt.title('Confusion Matrix for Personal Loan Prediction')
    plt.tight_layout()
    plt.savefig('confusion_matrix.png')

    # 5 - true cases
    print('\nQuestion 5: 306 accurately predicted cases where people accepted offers of a personal loan (TP)')
    print('and 30 cases inaccurately predicted cases where people actually accepted offers of a personal loan (FN)')
    print('so 336 total accepted offers on a personal loan.')

    # step 6: plotting the tree
    plt.figure(2, figsize=(10, 8))
    plot_tree(model_dt, feature_names=X.columns, filled=True)
    plt.title('Decision Tree for Personal Loan Prediction')
    plt.tight_layout()
    plt.savefig('decision tree - loans.png')

    # step 7: false negatives using confusion matrix
    print('\nQuestion 7: 30 cases where acceptors were classified as non-acceptors (FN)\n')

    # step 8: false positives using confusion matrix
    print('Question 8: 21 cases where non-acceptors were classified as acceptors (FP)\n')

    # step 9:  training accuracy score
    acc_score1 = model_dt.score(X_train, y_train)
    print('\ntraining accuracy score:', acc_score1)

    # step 9: test accuracy score
    acc_score2 = model_dt.score(X_test, y_test)
    print('\ntest accuracy score:', acc_score2)


if __name__ == '__main__':
    main()
