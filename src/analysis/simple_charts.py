
import os
import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path
from config import Config
import numpy as np

class SimpleCharts:

    def __init__(self, config_features_path: Path, figures_path: Path):
        self.config_features_path = config_features_path
        self.figures_path = figures_path
        self.boxplot_path = figures_path / 'boxplots'
        self.hist_path = figures_path / 'histograms'
        os.makedirs(self.boxplot_path, exist_ok=True)
        os.makedirs(self.hist_path, exist_ok=True)

    def print_boxplot(self, df_licit, df_illicit, df_without_unknown, df_all, feature:str):
        fig = plt.figure(figsize=(16, 6))
        
        # Criar grid: 4 boxplots em cima, tabela embaixo
        gs = fig.add_gridspec(2, 4, height_ratios=[3, 1], hspace=0.4)
        
        datasets = [
            (df_licit, 'Lícito', 0),
            (df_illicit, 'Ilícito', 1),
            (df_without_unknown, 'Lícito + Ilícito', 2),
            (df_all, 'Considerando Unknown', 3)
        ]
        
        stats_data = []
        labels = []
        
        for df, label, col in datasets:
            ax = fig.add_subplot(gs[0, col])
            bp = ax.boxplot(df[feature], widths=0.6, patch_artist=True)
            
            # Estilizar boxplot
            bp['boxes'][0].set_facecolor('lightblue')
            bp['boxes'][0].set_alpha(0.7)
            
            # Calcular estatísticas
            q1 = df[feature].quantile(0.25)
            q3 = df[feature].quantile(0.75)
            iqr = q3 - q1
            median = df[feature].median()
            
            labels.append(label)
            stats_data.append([q1, median, q3, iqr])
            
            ax.set_title(label, fontsize=12, fontweight='bold')
            ax.set_ylabel(feature if label == 'Lícito' else '')
            ax.grid(axis='y', alpha=0.3)
        
        # Transpor os dados para inverter linhas e colunas
        stats_transposed = list(zip(*stats_data))
        stats_formatted = [[f'{val:.2f}' for val in row] for row in stats_transposed]
        
        # Adicionar tabela
        ax_table = fig.add_subplot(gs[1, :])
        ax_table.axis('tight')
        ax_table.axis('off')
        
        table = ax_table.table(cellText=stats_formatted,
                            rowLabels=['Q1', 'Mediana', 'Q3', 'IQR'],
                            colLabels=labels,
                            cellLoc='center',
                            loc='center')
        table.auto_set_font_size(False)
        table.set_fontsize(9)
        table.scale(1, 1.5)
        
        plt.suptitle(f'Boxplots for feature: {feature}', fontsize=16, y=0.98)
        plt.savefig(self.boxplot_path / f'boxplot_{feature}.png', bbox_inches='tight', dpi=100)
        plt.close()

    def print_histogram_1(self, df_licit, df_illicit, df_without_unknown, df_all, feature:str):
        plt.figure(figsize=(16,4))
        
        plt.subplot(151); plt.hist(df_licit[feature].dropna(), bins=30, edgecolor='black')
        plt.subplot(152); plt.hist(df_illicit[feature].dropna(), bins=30, edgecolor='black')
        plt.subplot(153); plt.hist(df_without_unknown[feature].dropna(), bins=30, edgecolor='black')
        plt.subplot(154); plt.hist(df_all[feature].dropna(), bins=30, edgecolor='black')

        plt.suptitle(f'Histograms for feature: {feature}', fontsize=16)
        plt.savefig(self.hist_path / f'histogram_{feature}.png')
        plt.close()

    def print_histogram_2(self, df_licit, df_illicit, df_without_unknown, df_all, feature:str):
        fig, axes = plt.subplots(1, 4, figsize=(16, 5))
        
        datasets = [
            (df_licit, 'Lícito', axes[0]),
            (df_illicit, 'Ilícito', axes[1]),
            (df_without_unknown, 'Lícito + Ilícito', axes[2]),
            (df_all, 'All', axes[3])
        ]
        
        for df, label, ax in datasets:
            data = df[feature].dropna()
            
            ax.hist(data, bins=50, edgecolor='black', alpha=0.7, color='steelblue')
            ax.set_yscale('log')  # Escala logarítmica para ver caudas
            ax.set_title(label, fontsize=12, fontweight='bold')
            ax.set_xlabel(feature if label == 'Lícito' else '')
            ax.set_ylabel('Frequência (log)' if label == 'Lícito' else '')
            ax.grid(axis='y', alpha=0.3, linestyle='--')
            
            # Adicionar estatísticas
            mean_val = data.mean()
            median_val = data.median()
            ax.axvline(mean_val, color='red', linestyle='--', linewidth=1.5, label=f'Média: {mean_val:.2f}')
            ax.axvline(median_val, color='green', linestyle='--', linewidth=1.5, label=f'Mediana: {median_val:.2f}')
            ax.legend(fontsize=8, loc='upper right')
        
        plt.suptitle(f'Histogramas para feature: {feature}', fontsize=16, y=1.02)
        plt.tight_layout()
        plt.savefig(self.hist_path / f'histogram_{feature}.png', bbox_inches='tight', dpi=100)
        plt.close()

    def print_histogram_3(self, df_licit, df_illicit, df_without_unknown, df_all, feature:str):
        fig, axes = plt.subplots(1, 4, figsize=(16, 5))
        
        datasets = [
            (df_licit, 'Lícito', axes[0]),
            (df_illicit, 'Ilícito', axes[1]),
            (df_without_unknown, 'Lícito + Ilícito', axes[2]),
            (df_all, 'All', axes[3])
        ]
        
        for df, label, ax in datasets:
            data = df[feature].dropna()
            
            # Remover outliers extremos para melhor visualização
            q1 = data.quantile(0.01)
            q99 = data.quantile(0.99)
            data_filtered = data[(data >= q1) & (data <= q99)]
            
            ax.hist(data_filtered, bins=50, edgecolor='black', alpha=0.7, color='steelblue')
            ax.set_title(f'{label}\n(P1-P99: {q1:.2f} a {q99:.2f})', fontsize=10, fontweight='bold')
            ax.set_xlabel(feature if label == 'Lícito' else '')
            ax.set_ylabel('Frequência' if label == 'Lícito' else '')
            ax.grid(axis='y', alpha=0.3, linestyle='--')
            
            # Estatísticas
            mean_val = data.mean()
            median_val = data.median()
            ax.axvline(mean_val, color='red', linestyle='--', linewidth=1.5, alpha=0.7, label=f'Média: {mean_val:.2f}')
            ax.axvline(median_val, color='green', linestyle='--', linewidth=1.5, alpha=0.7, label=f'Mediana: {median_val:.2f}')
            ax.legend(fontsize=8, loc='upper right')
        
        plt.suptitle(f'Histogramas para feature: {feature} (1º ao 99º percentil)', fontsize=16, y=1.02)
        plt.tight_layout()
        plt.savefig(self.hist_path / f'histogram_{feature}.png', bbox_inches='tight', dpi=100)
        plt.close()

    def print_histogram_4(self, df_licit, df_illicit, df_without_unknown, df_all, feature:str):
        fig, axes = plt.subplots(1, 4, figsize=(16, 5))
        
        datasets = [
            (df_licit, 'Lícito', axes[0]),
            (df_illicit, 'Ilícito', axes[1]),
            (df_without_unknown, 'Lícito + Ilícito', axes[2]),
            (df_all, 'All', axes[3])
        ]
        
        for df, label, ax in datasets:
            data = df[feature].dropna()
            
            # Histograma com escala log
            n, bins, patches = ax.hist(data, bins=50, edgecolor='black', 
                                        alpha=0.6, color='steelblue')
            ax.set_yscale('log')
            
            # Adicionar KDE (densidade) se houver dados suficientes
            if len(data) > 10:
                from scipy import stats
                density = stats.gaussian_kde(data)
                xs = np.linspace(data.min(), data.max(), 200)
                # Escalar KDE para o histograma
                kde_scaled = density(xs) * len(data) * (bins[1] - bins[0])
                ax2 = ax.twinx()
                ax2.plot(xs, kde_scaled, 'r-', linewidth=2, label='Densidade', alpha=0.7)
                ax2.set_ylabel('Densidade' if label == 'All' else '', color='r')
                ax2.tick_params(axis='y', labelcolor='r')
                ax2.set_yscale('log')
            
            ax.set_title(label, fontsize=12, fontweight='bold')
            ax.set_xlabel(feature if label == 'Lícito' else '')
            ax.set_ylabel('Frequência (log)' if label == 'Lícito' else '')
            ax.grid(axis='y', alpha=0.3, linestyle='--')
            
            # Estatísticas básicas
            mean_val = data.mean()
            median_val = data.median()
            ax.axvline(mean_val, color='orange', linestyle='--', linewidth=1.5, 
                    alpha=0.8, label=f'μ={mean_val:.2f}')
            ax.axvline(median_val, color='green', linestyle='--', linewidth=1.5, 
                    alpha=0.8, label=f'Med={median_val:.2f}')
            ax.legend(fontsize=8, loc='upper right')
        
        plt.suptitle(f'Histogramas para feature: {feature}', fontsize=16, y=1.02)
        plt.tight_layout()
        plt.savefig(self.hist_path / f'histogram_{feature}.png', bbox_inches='tight', dpi=100)
        plt.close()

    def run(self):
        df = pd.read_csv(self.config_features_path)
        #node_ID, class
        features = df.columns.tolist()
        features.remove('node_ID')
        features.remove('class')

        for feature in features:
            df_licit = df[df['class'] == Config.Classes.LICIT]
            df_illicit = df[df['class'] == Config.Classes.ILLICIT]
            df_without_unknown = df[df['class'] != Config.Classes.UNKNOWN]
            df_all = df

            self.print_boxplot(df_licit, df_illicit,  df_without_unknown, df_all, feature)
            self.print_histogram_3(df_licit, df_illicit,  df_without_unknown, df_all, feature)
        
        print(f"Boxplots and Histograms saved in: {self.figures_path}")
