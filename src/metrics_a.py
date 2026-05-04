from sklearn.metrics import roc_auc_score, average_precision_score, precision_recall_curve, roc_curve
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import os
from config import Config

CLASSE_ILICITA = 1
CLASSE_LICITA = 2
CLASSE_UNKNOWN = 3


class MetricsA():
    """
    Classe para avaliar detector de anomalias não-supervisionado.
    
    IMPORTANTE: Este detector retorna scores MENORES para anomalias (ilícitas).
    A classe inverte automaticamente os scores para ranking (Precision@K, Recall@K).
    """
    
    def __init__(self, scores_sorted, address_to_class, figures_path, setup_name):
        """
        Args:
            scores_sorted: lista de tuplas (address, score) já ordenada
            address_to_class: dict {address: class}
            figures_path: caminho para salvar gráficos
            setup_name: nome da configuração para nomear arquivos
        """
        self.address_to_class = address_to_class
        self.figures_path = figures_path / 'metrics'
        self.setup_name = setup_name
        os.makedirs(self.figures_path, exist_ok=True)
        
        # Armazena scores originais
        self.scores_original = scores_sorted
        
        # INVERSÃO: scores menores = anomalias, então invertemos para ranking
        # Agora scores maiores (invertidos) = anomalias
        self.scores_inverted = [(addr, score) for addr, score in scores_sorted] # só trocar para 1-score ou score
        self.scores_inverted = sorted(self.scores_inverted, key=lambda x: x[1], reverse=True)
        
        # DataFrame com scores INVERTIDOS (para ranking)
        self.df_scores = self._define_df_scores()
        
        print(f"\n{'='*60}")
        print(f"Top 5 scores:")
        print(self.scores_inverted[:5])
        print()
        print(f"Bottom 5 scores:")
        asdf = len(self.scores_inverted) - 5
        print(self.scores_inverted[asdf:])
        print()
        print(self.df_scores.head())
        print()

        # Preparar para sklearn
        self.y_true, self.y_scores = self._prepare_for_sklearn(
            exclude_unknown=Config.remove_unknown_from_config
        )
        
        print(f"\n{'='*60}")
        print(f"Metrics initialized for: {setup_name}")
        print(f"Total addresses: {len(self.df_scores)}")
        print(f"Exclude unknown: {Config.remove_unknown_from_config}")
        print(f"Scores INVERTED for ranking (higher = more anomalous)")
        print(f"{'='*60}\n")

    def _define_df_scores(self):
        """
        Cria DataFrame com scores INVERTIDOS.
        Scores maiores agora = mais anômalos.
        """
        rows = []
        for address, score in self.scores_inverted:
            label = self.address_to_class.get(address)
            if label is not None:
                rows.append({
                    "address": address,
                    "score": score,
                    "class": label
                })
        
        df_scores = pd.DataFrame(rows)
        print("Class distribution:")
        print(df_scores["class"].value_counts())
        return df_scores

    def _prepare_for_sklearn(self, exclude_unknown=False):
        """
        Prepara dados para métricas do sklearn.
        
        Args:
            exclude_unknown: se True, remove classe UNKNOWN das métricas
        
        Returns:
            y_true: array binário (1=ilícita, 0=lícita)
            y_scores: array de scores (invertidos)
        """
        if exclude_unknown:
            self.df_bin = self.df_scores[
                self.df_scores["class"].isin([CLASSE_ILICITA, CLASSE_LICITA])
            ]
        else:
            self.df_bin = self.df_scores
        
        y_true = (self.df_bin["class"] == CLASSE_ILICITA).astype(int).values # Printar para ver se isso é aquela linha de true e false
        y_scores = self.df_bin["score"].values
        
        return y_true, y_scores # entender esses valores

    # ========== MÉTRICAS CORE ==========
    
    def auc_roc(self):
        """
        Area Under ROC Curve.
        
        | AUC     | Significado |
        | ------- | ----------- |
        | 0.5     | aleatório   |
        | 0.7–0.8 | razoável    |
        | 0.8–0.9 | bom         |
        | >0.9    | excelente   |
        
        NOTA: Com scores invertidos, esperamos AUC > 0.5
        """
        return roc_auc_score(self.y_true, self.y_scores)
    
    def average_precision(self):
        """
        Average Precision - área sob curva Precision-Recall.
        Métrica mais importante para ranking em datasets desbalanceados.
        
        Com scores invertidos, valores maiores = melhor.
        """
        return average_precision_score(self.y_true, self.y_scores)
    
    def max_f1(self):
        """
        Retorna o maior F1 possível variando o threshold.
        
        Returns:
            max_f1: melhor F1 score
            best_threshold: threshold que maximiza F1
        """
        precision, recall, thresholds = precision_recall_curve(self.y_true, self.y_scores)
        
        # Alinhar arrays (precision/recall têm 1 elemento a mais)
        precision = precision[:-1]
        recall = recall[:-1]
        
        f1_scores = 2 * (precision * recall) / (precision + recall + 1e-9)
        
        max_f1 = np.max(f1_scores)
        best_threshold = thresholds[np.argmax(f1_scores)]
        
        return max_f1, best_threshold

    def precision_at_k(self, k=10, positive_class=CLASSE_ILICITA):
        """
        Precisão nos top-K elementos (scores mais altos = invertidos).
        
        Métrica chave para detecção de anomalias: queremos alta precisão
        nos primeiros alertas.
        
        Args:
            k: número de elementos no topo
            positive_class: classe considerada positiva (default: ilícita)
        
        Returns:
            float: proporção de positivos nos top-K
        """
        if k > len(self.scores_inverted):
            k = len(self.scores_inverted)
        
        top_k = self.scores_inverted[:k]
        true_positives = sum(
            1 for address, _ in top_k 
            if self.address_to_class.get(address) == positive_class
        )
        
        return true_positives / k

    def precision_at_k_ignore_unknown(self, k, positive_class=CLASSE_ILICITA):
        """
        Precisão@K ignorando elementos UNKNOWN.
        Útil quando UNKNOWN não deve ser contado como erro.
        """
        if k > len(self.scores_inverted):
            k = len(self.scores_inverted)
            
        top_k = self.scores_inverted[:k]
        
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
        """
        Recall nos top-K elementos.
        Proporção de ilícitas capturadas nos top-K.
        
        Args:
            k: número de elementos no topo
        
        Returns:
            float: recall@k
        """
        if k > len(self.scores_inverted):
            k = len(self.scores_inverted)
            
        top_k = self.scores_inverted[:k]
        
        total_ilicitos = sum(
            1 for c in self.address_to_class.values() 
            if c == CLASSE_ILICITA
        )
        
        if total_ilicitos == 0:
            return 0.0
        
        tp = sum(
            1 for address, _ in top_k 
            if self.address_to_class.get(address) == CLASSE_ILICITA
        )
        
        return tp / total_ilicitos

    # ========== ANÁLISE DE SCORES ==========
    
    def scores_profile(self):
        """
        Análise detalhada da distribuição de scores por classe.
        Valida se a inversão está funcionando corretamente.
        """
        df_scores = self.df_scores
        
        print("\n" + "="*60)
        print("SCORE DISTRIBUTION ANALYSIS")
        print("="*60)
        
        print("\n1. Scores profile (all classes):")
        print(df_scores.groupby("class")["score"].describe())
        print('-'*60)
        
        df_bin = df_scores[df_scores["class"].isin([CLASSE_ILICITA, CLASSE_LICITA])]
        print("\n2. Scores profile (excluding UNKNOWN):")
        print(df_bin.groupby("class")["score"].describe())
        print('-'*60)
        
        df_ilicita = df_scores[df_scores["class"] == CLASSE_ILICITA]
        print("\n3. Ilícita score quantiles:")
        print(df_ilicita["score"].quantile([0.5, 0.75, 0.9, 0.95, 0.99]))
        print('-'*60)
        
        df_sorted = df_scores.sort_values("score", ascending=False)
        
        for top_n in [100, 500, 1000]:
            top_k = df_sorted.head(top_n)
            print(f"\n4. Top {top_n} score class distribution:")
            print(top_k["class"].value_counts(normalize=True))
            print(f"   Precision@{top_n}: {(top_k['class'] == CLASSE_ILICITA).mean():.4f}")
        print('-'*60)
        
        max_ilicita = df_scores[df_scores["class"] == CLASSE_ILICITA]["score"].max()
        min_licita = df_scores[df_scores["class"] == CLASSE_LICITA]["score"].min()
        mean_ilicita = df_scores[df_scores["class"] == CLASSE_ILICITA]["score"].mean()
        mean_licita = df_scores[df_scores["class"] == CLASSE_LICITA]["score"].mean()
        
        print(f"\n5. Score ranges (AFTER inversion):")
        print(f"   Max ILÍCITA:  {max_ilicita:.6f}")
        print(f"   Mean ILÍCITA: {mean_ilicita:.6f}")
        print(f"   Mean LÍCITA:  {mean_licita:.6f}")
        print(f"   Min LÍCITA:   {min_licita:.6f}")
        print(f"   ✓ Separation: {'GOOD' if mean_ilicita > mean_licita else 'BAD - CHECK INVERSION!'}")
        print('-'*60)
        
        print("\n" + "="*60 + "\n")

    # ========== GRÁFICOS ==========
    
    def plot_roc_curve(self):
        """
        ROC Curve: True Positive Rate vs False Positive Rate.
        Curva acima da diagonal = modelo melhor que aleatório.
        """
        fpr, tpr, _ = roc_curve(self.y_true, self.y_scores)
        auc = self.auc_roc()
        
        plt.figure(figsize=(8, 6))
        plt.plot(fpr, tpr, label=f"AUC = {auc:.3f}", linewidth=2)
        plt.plot([0, 1], [0, 1], 'k--', label='Random', linewidth=1)
        plt.xlabel("False Positive Rate", fontsize=12)
        plt.ylabel("True Positive Rate", fontsize=12)
        plt.title(f"ROC Curve - {self.setup_name}", fontsize=14)
        plt.legend(fontsize=11)
        plt.grid(alpha=0.3)
        plt.tight_layout()
        
        filepath = self.figures_path / f"{self.setup_name}_roc_curve.png"
        plt.savefig(filepath, dpi=150)
        plt.close()
        print(f"✓ Saved: {filepath}")

    def plot_precision_recall_curve(self):
        """
        Precision-Recall Curve.
        Mais informativa que ROC para datasets desbalanceados.
        """
        precision, recall, _ = precision_recall_curve(self.y_true, self.y_scores)
        ap = self.average_precision()
        
        plt.figure(figsize=(8, 6))
        plt.plot(recall, precision, label=f"AP = {ap:.3f}", linewidth=2)
        plt.xlabel("Recall", fontsize=12)
        plt.ylabel("Precision", fontsize=12)
        plt.title(f"Precision-Recall Curve - {self.setup_name}", fontsize=14)
        plt.legend(fontsize=11)
        plt.grid(alpha=0.3)
        plt.tight_layout()
        
        filepath = self.figures_path / f"{self.setup_name}_precision_recall_curve.png"
        plt.savefig(filepath, dpi=150)
        plt.close()
        print(f"✓ Saved: {filepath}")

    def plot_precision_at_k_curve(self):
        """
        Precision@K vs K.
        Mostra quão boa é a precisão nos primeiros K alertas.
        """
        ks = np.arange(10, min(5000, len(self.df_scores)), 50)
        df_sorted = self.df_scores.sort_values("score", ascending=False)
        
        p_at_k = []
        for k in ks:
            top_k = df_sorted.head(k)
            p = (top_k["class"] == CLASSE_ILICITA).mean()
            p_at_k.append(p)
        
        plt.figure(figsize=(10, 6))
        plt.plot(ks, p_at_k, linewidth=2)
        plt.xlabel("K (top elements)", fontsize=12)
        plt.ylabel("Precision@K", fontsize=12)
        plt.title(f"Precision@K - {self.setup_name}", fontsize=14)
        plt.grid(alpha=0.3)
        plt.tight_layout()
        
        filepath = self.figures_path / f"{self.setup_name}_precision_k.png"
        plt.savefig(filepath, dpi=150)
        plt.close()
        print(f"✓ Saved: {filepath}")

    def plot_recall_at_k_curve(self):
        """
        Recall@K vs K.
        Mostra quantas ilícitas são capturadas nos top-K.
        """
        max_k = min(50000, len(self.df_scores))
        ks = np.arange(100, max_k, 500)
        df_sorted = self.df_scores.sort_values("score", ascending=False)
        total_pos = (df_sorted["class"] == CLASSE_ILICITA).sum()
        
        r_at_k = []
        for k in ks:
            top_k = df_sorted.head(k)
            tp = (top_k["class"] == CLASSE_ILICITA).sum()
            r_at_k.append(tp / total_pos if total_pos > 0 else 0)
        
        plt.figure(figsize=(10, 6))
        plt.plot(ks, r_at_k, linewidth=2)
        plt.xlabel("K (top elements)", fontsize=12)
        plt.ylabel("Recall@K", fontsize=12)
        plt.title(f"Recall@K - {self.setup_name}", fontsize=14)
        plt.grid(alpha=0.3)
        plt.tight_layout()
        
        filepath = self.figures_path / f"{self.setup_name}_recall_k.png"
        plt.savefig(filepath, dpi=150)
        plt.close()
        print(f"✓ Saved: {filepath}")

    def plot_scores_distribution(self):
        """
        Histograma de scores por classe.
        Mostra separação entre ilícitas e lícitas.
        """
        plt.figure(figsize=(10, 6))
        
        classes_to_plot = [
            (CLASSE_ILICITA, "Ilícita", "red"),
            (CLASSE_LICITA, "Lícita", "green"),
        ]
        
        if (self.df_scores["class"] == CLASSE_UNKNOWN).any():
            classes_to_plot.append((CLASSE_UNKNOWN, "Unknown", "gray"))
        
        for cls, label, color in classes_to_plot:
            subset = self.df_scores[self.df_scores["class"] == cls]["score"]
            if len(subset) > 0:
                plt.hist(subset, bins=100, alpha=0.5, density=True, 
                        label=f"{label} (n={len(subset)})", color=color)
        
        plt.xlabel("Score (inverted)", fontsize=12)
        plt.ylabel("Density", fontsize=12)
        plt.title(f"Score Distribution - {self.setup_name}", fontsize=14)
        plt.legend(fontsize=11)
        plt.grid(alpha=0.3)
        plt.tight_layout()
        
        filepath = self.figures_path / f"{self.setup_name}_score_distribution.png"
        plt.savefig(filepath, dpi=150)
        plt.close()
        print(f"✓ Saved: {filepath}")

    def plot_all_graphs(self):
        """Gera todos os gráficos de avaliação."""
        print(f"\n{'='*60}")
        print(f"Generating plots for: {self.setup_name}")
        print(f"{'='*60}")
        
        self.plot_roc_curve()
        self.plot_precision_recall_curve()
        self.plot_precision_at_k_curve()
        self.plot_recall_at_k_curve()
        self.plot_scores_distribution()
        
        print(f"{'='*60}\n")

    # ========== SUMÁRIO DE MÉTRICAS ==========
    
    def get_metrics(self):
        """
        Retorna dicionário com todas as métricas principais.
        """
        auc_roc = self.auc_roc()
        avg_precision = self.average_precision()
        max_f1, best_threshold = self.max_f1()
        
        metrics = {
            "AUC-ROC": auc_roc,
            "Average Precision": avg_precision,
            "Max F1": max_f1,
            "Best Threshold": best_threshold,
        }
        
        # Precision@K para vários valores de K
        for k in [10, 50, 100, 200, 300, 400, 500, 1000]:
            if k <= len(self.scores_inverted):
                metrics[f"Precision@{k}"] = self.precision_at_k(k=k)
        
        # Recall@K para valores maiores
        for k in [100, 500, 1000, 5000]:
            if k <= len(self.scores_inverted):
                metrics[f"Recall@{k}"] = self.recall_at_k(k=k)
        
        return metrics
    
    def print_metrics(self):
        """
        Imprime todas as métricas de forma organizada.
        """
        metrics = self.get_metrics()
        
        print(f"\n{'='*60}")
        print(f"METRICS SUMMARY: {self.setup_name}")
        print(f"{'='*60}\n")
        
        print("Classification Metrics:")
        print(f"  AUC-ROC:            {metrics['AUC-ROC']:.4f}")
        print(f"  Average Precision:  {metrics['Average Precision']:.4f}")
        print(f"  Max F1:             {metrics['Max F1']:.4f}")
        print(f"  Best Threshold:     {metrics['Best Threshold']:.4f}")
        
        print("\nRanking Metrics (Precision@K):")
        for k in [10, 50, 100, 200, 300, 400, 500, 1000]:
            key = f"Precision@{k}"
            if key in metrics:
                print(f"  {key:20s} {metrics[key]:.4f}")
        
        print("\nRecall@K:")
        for k in [100, 500, 1000, 5000]:
            key = f"Recall@{k}"
            if key in metrics:
                print(f"  {key:20s} {metrics[key]:.4f}")
        
        print(f"\n{'='*60}\n")
        
        return metrics