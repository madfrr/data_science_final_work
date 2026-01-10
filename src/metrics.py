from sklearn.metrics import roc_auc_score, average_precision_score, precision_recall_curve, roc_curve
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


CLASSE_ILICITA = 1
CLASSE_LICITA = 2
CLASSE_UNKNOWN = 3


class Metrics():
    def __init__(self, scores_sorted, address_to_class):
        self.scores = scores_sorted
        self.address_to_class = address_to_class
        self.df_scores = self._define_df_scores()
        self.y_true, self.y_scores = self._prepare_for_sklearn(exclude_unknown=True)

    def _define_df_scores(self):
        rows = []

        for address, score in self.scores:
            label = self.address_to_class.get(address)
            if label is not None:
                rows.append({
                    "address": address,
                    "score": score,
                    "class": label
                })

        return pd.DataFrame(rows)

    def _prepare_for_sklearn(self, exclude_unknown=False):
        self.df_bin = self.df_scores[self.df_scores["class"].isin([CLASSE_ILICITA, CLASSE_LICITA])] if exclude_unknown else self.df_scores
        y_true = (self.df_bin["class"] == CLASSE_ILICITA).astype(int).values
        y_scores = self.df_bin["score"].values

        return y_true, y_scores

    def plot_roc_curve(self):
        '''
        Curva acima da diagonal, mas não muito íngreme → separação média.
        '''
        fpr, tpr, _ = roc_curve(self.y_true, self.y_scores)
        auc = roc_auc_score(self.y_true, self.y_scores)

        plt.figure()
        plt.plot(fpr, tpr, label=f"AUC = {auc:.3f}")
        plt.plot([0, 1], [0, 1], linestyle="--")
        plt.xlabel("False Positive Rate")
        plt.ylabel("True Positive Rate")
        plt.title("ROC Curve")
        plt.legend()
        plt.show()


    def plot_precision_recall_curve(self):
        '''
        Leitura esperada
        - Precision cai rápido
        - Não existe região com precision alta e recall razoável
        - Confirma: ranking fraco no topo
        '''
        precision, recall, _ = precision_recall_curve(self.y_true, self.y_scores)
        ap = average_precision_score(self.y_true, self.y_scores)

        plt.figure()
        plt.plot(recall, precision, label=f"AP = {ap:.3f}")
        plt.xlabel("Recall")
        plt.ylabel("Precision")
        plt.title("Precision–Recall Curve")
        plt.legend()
        plt.show()

    def plot_precision_at_k_curve(self):
        '''
        Leitura esperada
        - Linha quase colada no zero
        - Visualmente encerra qualquer debate sobre alertas top-K
        '''

        ks = np.arange(10, 5000, 50)
        df_sorted = self.df_scores.sort_values("score", ascending=False)
        p_at_k = []

        for k in ks:
            top_k = df_sorted.head(k)
            p = (top_k["class"] == CLASSE_ILICITA).mean()
            p_at_k.append(p)

        plt.figure()
        plt.plot(ks, p_at_k)
        plt.xlabel("K")
        plt.ylabel("Precision@K")
        plt.title("Precision@K vs K")
        plt.show()

    def plot_recall_at_k_curve(self):
        '''
        📌 Leitura esperada
        - Recall cresce lentamente
        - Modelo só “funciona” em K grandes
        - Isso justifica uso como pré-filtro
        '''
        ks = np.arange(100, 50000, 500)
        df_sorted = self.df_scores.sort_values("score", ascending=False)
        total_pos = (df_sorted["class"] == CLASSE_ILICITA).sum()
        r_at_k = []

        for k in ks:
            top_k = df_sorted.head(k)
            tp = (top_k["class"] == CLASSE_ILICITA).sum()
            r_at_k.append(tp / total_pos)

        plt.figure()
        plt.plot(ks, r_at_k)
        plt.xlabel("K")
        plt.ylabel("Recall@K")
        plt.title("Recall@K vs K")
        plt.show()

    def plot_scores_distribution(self):
        plt.figure()
        for cls, label in [(1, "Ilícita"), (2, "Lícita"), (3, "Unknown")]:
            subset = self.df_scores[self.df_scores["class"] == cls]["score"]
            plt.hist(subset, bins=100, alpha=0.5, density=True, label=label)

        plt.xlabel("Score")
        plt.ylabel("Density")
        plt.title("Score Distribution by Class")
        plt.legend()
        plt.show()

    def plot_all_graphs(self):
        self.plot_roc_curve()
        self.plot_precision_recall_curve()
        self.plot_precision_at_k_curve()
        self.plot_recall_at_k_curve()
        self.plot_scores_distribution()

    def auc_roc(self):
        """
        | AUC     | Significado |
        | ------- | ----------- |
        | 0.5     | aleatório   |
        | 0.7–0.8 | razoável    |
        | 0.8–0.9 | bom         |
        | >0.9    | excelente   |
        Em fraude, AUC alto não garante bom Precision@K.
        """
        return roc_auc_score(self.y_true, self.y_scores)
    
    def average_precision(self):
        """
        AP é a área sob a curva de precision-recall.
        https://scikit-learn.org/stable/modules/generated/sklearn.metrics.average_precision_score.html
        """
        return average_precision_score(self.y_true, self.y_scores)
    
    def max_f1(self):
        """
        Retorna o maior F1 possível variando o threshold.
        """
        precision, recall, thresholds = precision_recall_curve(self.y_true, self.y_scores)

        f1_scores = 2 * (precision * recall) / (precision + recall + 1e-9)

        max_f1 = np.max(f1_scores)
        best_threshold = thresholds[np.argmax(f1_scores[:-1])]
        return max_f1, best_threshold

    def precision_at_k(self, k=10, positive_class=CLASSE_ILICITA):
        """
        scores: lista de (address, score), já ordenada desc
        address_to_class: dict {address: class}
        k: int
        positive_class: classe considerada positiva
        """
        top_k = self.scores[:k]

        true_positives = 0

        for address, _ in top_k:
            if self.address_to_class.get(address) == positive_class:
                true_positives += 1

        return true_positives / k

    def precision_at_k_ignore_unknown(self, k, positive_class=CLASSE_ILICITA):
        top_k = self.scores[:k]

        valid = 0
        true_positives = 0

        for address, _ in top_k:
            label = self.address_to_class.get(address)
            if label == CLASSE_UNKNOWN or label is None:
                continue

            valid += 1
            if label == positive_class:
                true_positives += 1

        if valid == 0:
            return 0.0

        return true_positives / valid
    

    def recall_at_k(self, k):
        top_k = self.scores[:k]

        total_ilicitos = sum(
            1 for c in self.address_to_class.values() if c == CLASSE_ILICITA
        )

        if total_ilicitos == 0:
            return 0.0

        tp = 0
        for address, _ in top_k:
            if self.address_to_class.get(address) == CLASSE_ILICITA:
                tp += 1

        return tp / total_ilicitos
    
    def scores_profile_from_positive_class(self):
        df_scores = self.df_scores
        print("Scores profile:")
        print(df_scores.groupby("class")["score"].describe())
        print('-'*40)
        
        df_bin = df_scores[df_scores["class"].isin([1, 2])]
        print("Scores profile (excluding UNKNOWN):")        
        print(df_bin.groupby("class")["score"].describe())
        df_ilicita = df_scores[df_scores["class"] == 1]
        print('-'*40)
        
        print("Ilicita score quantiles:")
        print(df_ilicita["score"].quantile([0.5, 0.75, 0.9, 0.95, 0.99]))
        print('-'*40)

        df_scores_sorted = df_scores.sort_values("score", ascending=False)

        top_1000 = df_scores_sorted.head(1000)
        print("Top 1000 score class distribution:")
        print(top_1000["class"].value_counts(normalize=True))
        print('-'*40)
        
        max_ilicita = df_scores[df_scores["class"] == 1]["score"].max()
        min_licita = df_scores[df_scores["class"] == 2]["score"].min()

        print(f"max_ilicita: {max_ilicita}, min_licita: {min_licita}")
        print('-'*40)
        
        print('Inverting scores:')
        y_score_inv = [1 - s for s in self.y_scores]
        print("AUC inverted:", roc_auc_score(self.y_true, y_score_inv))
        print("AP inverted:", average_precision_score(self.y_true, y_score_inv))
        print('-'*40)

        print('Negative scores:')
        y_score_neg = [-s for s in self.y_scores]
        print("AUC from neg scores:", roc_auc_score(self.y_true, y_score_neg))
        print("AP from neg scores:", average_precision_score(self.y_true, y_score_neg))
        print('-'*40)

    def get_metrics(self):
        auc_roc = self.auc_roc()
        avg_precision = self.average_precision()
        max_f1, best_threshold = self.max_f1()
        precision_at_10 = self.precision_at_k(k=10)
        precision_at_50 = self.precision_at_k(k=50)
        precision_at_100 = self.precision_at_k(k=100)
        precision_at_200 = self.precision_at_k(k=200)
        precision_at_300 = self.precision_at_k(k=300)
        precision_at_400 = self.precision_at_k(k=400)
        precision_at_500 = self.precision_at_k(k=500)

        return {
            "AUC-ROC": auc_roc,
            "Average Precision": avg_precision,
            "Max F1": max_f1,
            "Best Threshold": best_threshold,
            "Precision@10": precision_at_10,
            "Precision@50": precision_at_50,
            "Precision@100": precision_at_100,
            "Precision@200": precision_at_200,
            "Precision@300": precision_at_300,
            "Precision@400": precision_at_400,
            "Precision@500": precision_at_500,
        }
    
    def print_metrics(self):
        metrics = self.get_metrics()
        for metric_name, value in metrics.items():
            print(f"{metric_name}: {value:.4f}")
    
