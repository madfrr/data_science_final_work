import pandas as pd


file_names = [
        "wallets_features.csv",
        "wallets_classes.csv",
        "wallets_features_classes_combined.csv",
        "AddrAddr_edgelist.csv",
        "AddrTx_edgelist.csv",
        "TxAddr_edgelist.csv",
        "txs_classes.csv",
        "txs_edgelist.csv",
        "txs_features.csv"
    ]

CLASSE_ILICITA = 1
CLASSE_LICITA = 2
CLASSE_UNKNOWN = 3

class Validations():
    """
    - Verificar se a wallets_features_classes_combined.csv está consistente com a wallets_features.csv e wallets_classes.csv
        - Verificar conjunto de colunas
        - Verificar conjunto de carteiras com count se ta tudo igual
        - Verificar se a carteira + ilicito está batendo com wallet_classes.csv
    
    - Verificar se a tabela AddrAddr_edgelist.csv está consistente com a TxAddr_edgelist.csv e a AddrTx_edgelist.csv
        - Se tiver, podemos usar a AddrAddr_edgelist.csv

    - Verificar se toda transação ilicita foi feita por um endereço ilicito
        agregar as tabelas AddrTx_edgelist e TxAddr_edgelist
        - Para cada transação na txs_classes.csv que for ilicita:
            - Verificar se algum dos endereços de entrada ou saída é ilicito

    - Entender se uma transação pode ser feita entre vários endereços de entrada e vários de saída???
        - Da pra fazer isso com a AddrTx_edgelist e TxAddr_edgelist, dai validando com a txs_features com in and out
        - Para cada transação no trx_features que tiver in_txs_degree e out_txs_degree maior que 1:
            - Verificar a qtd de endereços na AddrTx_edgelist para aquela transação coincidem com in_txs_degree
            - Verificar a qtd de endereços na TxAddr_edgelist para aquela transação coincidem com out_txs_degree
    """
    def __init__(self, data_path, data_dir = "data_selected_columns"):
        self.path = data_path / data_dir

    def validate_wallets_features_classes_combined(self):
        print(f"Validating wallets_features_classes_combined in {self.path}")
        wallets_features = pd.read_parquet(self.path / "wallets_features.parquet", columns=["address"])
        wallets_classes = pd.read_parquet(self.path / "wallets_classes.parquet", columns=["address", "class"])
        wallets_features_classes_combined = pd.read_parquet(self.path / "wallets_features_classes_combined.parquet", columns=["address", "class", "time_step"])

        wallets_set = set(wallets_features["address"])
        wallets_classes_set = set(wallets_classes["address"])
        wallets_combined_set = set(wallets_features_classes_combined["address"])
        if wallets_set == wallets_combined_set == wallets_classes_set:
            print("  ✓ wallets_features, wallets_classes and wallets_features_classes_combined have the same addresses")
        else:
            print("  ✗ Warning: wallets_features, wallets_classes and wallets_features_classes_combined have different addresses")

        df_wallets_combined = wallets_features_classes_combined.sort_values('time_step').groupby('address', as_index=False).last()

        # Comparar com outro dataframe
        # Opção 1: Verificar se são idênticos (mesmos addresses e classes)
        if df_wallets_combined[['address', 'class']].equals(wallets_classes[['address', 'class']]):
            print("  ✓ wallets_features_classes_combined classes match wallets_classes")
        else:
            print("  ✗ Warning: wallets_features_classes_combined classes do not match wallets_classes")

        return self

    def validate_addraddr_edgelist(self):
        print(f"Validating AddrAddr_edgelist in {self.path}")

        addr_addr = pd.read_parquet(self.path / "AddrAddr_edgelist.parquet", columns=["input_address", "output_address"])
        addr_tx = pd.read_parquet(self.path / "AddrTx_edgelist.parquet", columns=["input_address", "tx_id"])
        tx_addr = pd.read_parquet(self.path / "TxAddr_edgelist.parquet", columns=["tx_id", "output_address"])

        print("=== VERIFICAÇÃO DE CONSISTÊNCIA ===\n")

        # 1. Verificar tamanhos
        print("1. TAMANHOS DOS DATASETS")
        print(f"AddrAddr: {len(addr_addr):,} edges")
        print(f"AddrTx:   {len(addr_tx):,} edges")
        print(f"TxAddr:   {len(tx_addr):,} edges")

        # 2. Verificar se AddrAddr é derivado de AddrTx → TxAddr
        print("\n2. VERIFICAÇÃO: AddrAddr = AddrTx JOIN TxAddr")

        # Reconstruir AddrAddr a partir dos outros dois
        addr_addr_reconstruido = addr_tx.merge(
            tx_addr,
            on='tx_id',
            how='inner'
        )

        print(f"AddrAddr reconstruído: {len(addr_addr_reconstruido):,} edges")

        # Comparar conjuntos de edges
        edges_original = set(zip(addr_addr['input_address'], addr_addr['output_address']))
        edges_reconstruido = set(zip(addr_addr_reconstruido['input_address'], 
                                    addr_addr_reconstruido['output_address']))

        apenas_original = edges_original - edges_reconstruido
        apenas_reconstruido = edges_reconstruido - edges_original

        print(f"Edges apenas no original: {len(apenas_original):,}")
        print(f"Edges apenas no reconstruído: {len(apenas_reconstruido):,}")
        print(f"Edges em ambos: {len(edges_original & edges_reconstruido):,}")

        consistente_estrutura = len(apenas_original) == 0 and len(apenas_reconstruido) == 0
        print(f"{'✅' if consistente_estrutura else '❌'} Estrutura consistente? {consistente_estrutura}")
        return self
    
    def validate_illicit_transactions_with_addresses(self):
        print(f"Validating illicit transactions with addresses in {self.path}")
        
        addr_tx = pd.read_parquet(self.path / "AddrTx_edgelist.parquet", columns=["input_address", "tx_id"])
        tx_addr = pd.read_parquet(self.path / "TxAddr_edgelist.parquet", columns=["tx_id", "output_address"])
        wallets_classes = pd.read_parquet(self.path / "wallets_classes.parquet", columns=["address", "class"])
        txs_classes = pd.read_parquet(self.path / "txs_classes.parquet", columns=["tx_id", "class"])

        print("1. DISTRIBUIÇÃO DE CLASSES")
        print("\nWallets:")
        print(wallets_classes['class'].value_counts().sort_index())
        print(f"Total wallets: {len(wallets_classes):,}")

        print("\nTransações:")
        print(txs_classes['class'].value_counts().sort_index())
        print(f"Total transações: {len(txs_classes):,}")

        # 2. Adicionar classes aos edges
        print("\n2. ENRIQUECENDO EDGES COM CLASSES")

        # AddrTx com classe do address e da transação
        addr_tx_enriched = addr_tx.merge(
            wallets_classes,
            left_on='input_address',
            right_on='address',
            how='left'
        ).rename(columns={'class': 'input_addr_class'}).drop(columns=['address'])

        addr_tx_enriched = addr_tx_enriched.merge(
            txs_classes,
            on='tx_id',
            how='left'
        ).rename(columns={'class': 'tx_class'})

        # TxAddr com classe do address e da transação
        tx_addr_enriched = tx_addr.merge(
            txs_classes,
            on='tx_id',
            how='left'
        ).rename(columns={'class': 'tx_class'})

        tx_addr_enriched = tx_addr_enriched.merge(
            wallets_classes,
            left_on='output_address',
            right_on='address',
            how='left'
        ).rename(columns={'class': 'output_addr_class'}).drop(columns=['address'])

        print(f"✓ AddrTx enriquecido: {len(addr_tx_enriched):,} edges")
        print(f"✓ TxAddr enriquecido: {len(tx_addr_enriched):,} edges")

        print("Distribuição de classes:")
        print(txs_classes["class"].value_counts().reset_index(
            name="count"
        ).rename(columns={"index": "class"}))
        print()

        txs_ilicitas = txs_classes[txs_classes['class'] == CLASSE_ILICITA]['tx_id']
        print(f"\nTotal de transações ilícitas: {len(txs_ilicitas):,}")

        # Para cada transação ilícita, verificar inputs
        inputs_tx_ilicitas = addr_tx_enriched[addr_tx_enriched['tx_id'].isin(txs_ilicitas)]
        
        # Para cada transação ilícita, verificar outputs
        outputs_tx_ilicitas = tx_addr_enriched[tx_addr_enriched['tx_id'].isin(txs_ilicitas)]
        
        # Contar inputs ilícitos
        inputs_ilicitos = inputs_tx_ilicitas[inputs_tx_ilicitas['input_addr_class'] == CLASSE_ILICITA]
        inputs_licitos = inputs_tx_ilicitas[inputs_tx_ilicitas['input_addr_class'] != CLASSE_ILICITA]
        inputs_sem_classe = inputs_tx_ilicitas[inputs_tx_ilicitas['input_addr_class'].isna()]
        
        print(f"\n--- INPUTS de transações ilícitas ---")
        print(f"Ilícitos: {len(inputs_ilicitos):,} ({len(inputs_ilicitos)/len(inputs_tx_ilicitas)*100:.1f}%)")
        print(f"Lícitos: {len(inputs_licitos):,} ({len(inputs_licitos)/len(inputs_tx_ilicitas)*100:.1f}%)")
        print(f"Sem classe: {len(inputs_sem_classe):,} ({len(inputs_sem_classe)/len(inputs_tx_ilicitas)*100:.1f}%)")
        
        # Contar outputs ilícitos
        outputs_ilicitos = outputs_tx_ilicitas[outputs_tx_ilicitas['output_addr_class'] == CLASSE_ILICITA]
        outputs_licitos = outputs_tx_ilicitas[outputs_tx_ilicitas['output_addr_class'] != CLASSE_ILICITA]
        outputs_sem_classe = outputs_tx_ilicitas[outputs_tx_ilicitas['output_addr_class'].isna()]
        
        print(f"\n--- OUTPUTS de transações ilícitas ---")
        print(f"Ilícitos: {len(outputs_ilicitos):,} ({len(outputs_ilicitos)/len(outputs_tx_ilicitas)*100:.1f}%)")
        print(f"Lícitos: {len(outputs_licitos):,} ({len(outputs_licitos)/len(outputs_tx_ilicitas)*100:.1f}%)")
        print(f"Sem classe: {len(outputs_sem_classe):,} ({len(outputs_sem_classe)/len(outputs_tx_ilicitas)*100:.1f}%)")
        
        # Verificar transações ilícitas SEM nenhum endereço ilícito
        print("\n--- ANÁLISE POR TRANSAÇÃO ---")
        
        # Para cada tx ilícita, verificar se tem PELO MENOS um address ilícito
        txs_com_input_ilicito = set(inputs_ilicitos['tx_id'].unique())
        txs_com_output_ilicito = set(outputs_ilicitos['tx_id'].unique())
        
        txs_com_algum_addr_ilicito = txs_com_input_ilicito | txs_com_output_ilicito
        
        txs_ilicitas_set = set(txs_ilicitas)
        txs_sem_addr_ilicito = txs_ilicitas_set - txs_com_algum_addr_ilicito
        
        if len(txs_sem_addr_ilicito) > 0:
            print(f"\n⚠️  INCONSISTÊNCIA DETECTADA!")
            print(f"    {len(txs_sem_addr_ilicito)} transações ilícitas não têm nenhum endereço ilícito")
            print(f"    Isso representa {len(txs_sem_addr_ilicito)/len(txs_ilicitas)*100:.1f}% das transações ilícitas")
            
            # Mostrar exemplos
            print("\n    Exemplos de transações problemáticas:")
            for tx_id in list(txs_sem_addr_ilicito)[:5]:
                inputs = inputs_tx_ilicitas[inputs_tx_ilicitas['tx_id'] == tx_id]
                outputs = outputs_tx_ilicitas[outputs_tx_ilicitas['tx_id'] == tx_id]
                print(f"\n    TxId: {tx_id}")
                print(f"      Inputs: {list(inputs['input_addr_class'].unique())}")
                print(f"      Outputs: {list(outputs['output_addr_class'].unique())}")
        else:
            print(f"\n✅ CONSISTENTE: Todas as transações ilícitas têm pelo menos um endereço ilícito")

        return self
    
    def validate_transaction_degrees(self):
        print(f"Validating transaction degrees in {self.path}")
        addr_tx = pd.read_parquet(self.path / "AddrTx_edgelist.parquet", columns=["input_address", "tx_id"])
        tx_addr = pd.read_parquet(self.path / "TxAddr_edgelist.parquet", columns=["tx_id", "output_address"])
        txs_features = pd.read_parquet(self.path / "txs_features.parquet", columns=["tx_id", "time_step", "in_txs_degree", "out_txs_degree"])

        print("=== VALIDAÇÃO DE IN/OUT DEGREES ===\n")

        # 1. Informações básicas
        print("1. INFORMAÇÕES BÁSICAS")
        print(f"Total transações em txs_features: {len(txs_features):,}")
        print(f"Total transações únicas: {txs_features['tx_id'].nunique():,}")
        print(f"Timesteps: {txs_features['Time step'].min()} a {txs_features['Time step'].max()}")

        print("\n2. EXTRAINDO ÚLTIMO TIMESTEP POR TRANSAÇÃO")

        txs_ultimo_timestep = (txs_features
            .sort_values('time_step')
            .groupby('tx_id', as_index=False)
            .last()
        )

        print(f"Transações após filtrar último timestep: {len(txs_ultimo_timestep):,}")

        print("\n3. CALCULANDO DEGREES REAIS DAS EDGELISTS")

        # In-degree: quantidade de input addresses por transação
        in_degree_real = addr_tx.groupby('tx_id').size().reset_index(name='in_degree_real')

        # Out-degree: quantidade de output addresses por transação
        out_degree_real = tx_addr.groupby('tx_id').size().reset_index(name='out_degree_real')

        print(f"Transações com in_degree calculado: {len(in_degree_real):,}")
        print(f"Transações com out_degree calculado: {len(out_degree_real):,}")

        # 4. Merge com txs_features
        print("\n4. COMPARANDO COM TXS_FEATURES")

        comparacao = txs_ultimo_timestep.merge(
            in_degree_real,
            on='tx_id',
            how='outer',
            indicator='_merge_in'
        ).merge(
            out_degree_real,
            on='tx_id',
            how='outer',
            indicator='_merge_out'
        )

        # Renomear colunas para clareza
        comparacao = comparacao.rename(columns={
            'in_txs_degree': 'in_degree_features',
            'out_txs_degree': 'out_degree_features'
        })

        print("\n5. COMPARAÇÃO DE VALORES")

        # Filtrar apenas transações com ambos os valores
        comparacao_valida = comparacao[
            comparacao['in_degree_features'].notna() &
            comparacao['in_degree_real'].notna() &
            comparacao['out_degree_features'].notna() &
            comparacao['out_degree_real'].notna()
        ].copy()

        print(f"Transações com ambos os valores: {len(comparacao_valida):,}")

        # Verificar igualdade (considerando possível conversão float/int)
        comparacao_valida['in_degree_match'] = (
            comparacao_valida['in_degree_features'] == comparacao_valida['in_degree_real']
        )
        comparacao_valida['out_degree_match'] = (
            comparacao_valida['out_degree_features'] == comparacao_valida['out_degree_real']
        )

        in_matches = comparacao_valida['in_degree_match'].sum()
        out_matches = comparacao_valida['out_degree_match'].sum()
        total_validas = len(comparacao_valida)

        print(f"\n--- IN-DEGREE ---")
        print(f"Matches: {in_matches:,} ({in_matches/total_validas*100:.2f}%)")
        print(f"Diferenças: {total_validas - in_matches:,} ({(total_validas - in_matches)/total_validas*100:.2f}%)")

        print(f"\n--- OUT-DEGREE ---")
        print(f"Matches: {out_matches:,} ({out_matches/total_validas*100:.2f}%)")
        print(f"Diferenças: {total_validas - out_matches:,} ({(total_validas - out_matches)/total_validas*100:.2f}%)")

        # 7. Análise das diferenças
        print("\n7. ANÁLISE DAS DIFERENÇAS")

        # In-degree diferenças
        in_diferencas = comparacao_valida[~comparacao_valida['in_degree_match']].copy()
        if len(in_diferencas) > 0:
            in_diferencas['in_diff'] = (
                in_diferencas['in_degree_features'] - in_diferencas['in_degree_real']
            )
            
            print(f"\nIN-DEGREE - Estatísticas das diferenças:")
            print(f"  Média: {in_diferencas['in_diff'].mean():.2f}")
            print(f"  Mediana: {in_diferencas['in_diff'].median():.2f}")
            print(f"  Mín: {in_diferencas['in_diff'].min():.0f}, Máx: {in_diferencas['in_diff'].max():.0f}")
            print(f"  Std: {in_diferencas['in_diff'].std():.2f}")
            
            print(f"\n  Exemplos de diferenças:")
            exemplos = in_diferencas[['txId', 'Time step', 'in_degree_features', 'in_degree_real', 'in_diff']].head(10)
            print(exemplos.to_string(index=False))

        # Out-degree diferenças
        out_diferencas = comparacao_valida[~comparacao_valida['out_degree_match']].copy()
        if len(out_diferencas) > 0:
            out_diferencas['out_diff'] = (
                out_diferencas['out_degree_features'] - out_diferencas['out_degree_real']
            )
            
            print(f"\nOUT-DEGREE - Estatísticas das diferenças:")
            print(f"  Média: {out_diferencas['out_diff'].mean():.2f}")
            print(f"  Mediana: {out_diferencas['out_diff'].median():.2f}")
            print(f"  Mín: {out_diferencas['out_diff'].min():.0f}, Máx: {out_diferencas['out_diff'].max():.0f}")
            print(f"  Std: {out_diferencas['out_diff'].std():.2f}")
            
            print(f"\n  Exemplos de diferenças:")
            exemplos = out_diferencas[['txId', 'Time step', 'out_degree_features', 'out_degree_real', 'out_diff']].head(10)
            print(exemplos.to_string(index=False))

        # 8. Estatísticas gerais dos degrees
        print("\n8. ESTATÍSTICAS GERAIS DOS DEGREES")

        print("\nIN-DEGREE:")
        print(f"  Features - Média: {comparacao_valida['in_degree_features'].mean():.2f}, Mediana: {comparacao_valida['in_degree_features'].median():.0f}")
        print(f"  Real     - Média: {comparacao_valida['in_degree_real'].mean():.2f}, Mediana: {comparacao_valida['in_degree_real'].median():.0f}")

        print("\nOUT-DEGREE:")
        print(f"  Features - Média: {comparacao_valida['out_degree_features'].mean():.2f}, Mediana: {comparacao_valida['out_degree_features'].median():.0f}")
        print(f"  Real     - Média: {comparacao_valida['out_degree_real'].mean():.2f}, Mediana: {comparacao_valida['out_degree_real'].median():.0f}")

        # 9. Verificar transações específicas problemáticas
        print("\n9. TRANSAÇÕES PROBLEMÁTICAS")

        # Transações com grandes discrepâncias (> 5 de diferença)
        if len(in_diferencas) > 0:
            in_grandes_dif = in_diferencas[abs(in_diferencas['in_diff']) > 5]
            if len(in_grandes_dif) > 0:
                print(f"\n⚠️  {len(in_grandes_dif):,} transações com diferença > 5 no in_degree")
                print("   Exemplos:")
                print(in_grandes_dif[['txId', 'in_degree_features', 'in_degree_real', 'in_diff']].head(5).to_string(index=False))

        if len(out_diferencas) > 0:
            out_grandes_dif = out_diferencas[abs(out_diferencas['out_diff']) > 5]
            if len(out_grandes_dif) > 0:
                print(f"\n⚠️  {len(out_grandes_dif):,} transações com diferença > 5 no out_degree")
                print("   Exemplos:")
                print(out_grandes_dif[['txId', 'out_degree_features', 'out_degree_real', 'out_diff']].head(5).to_string(index=False))

        # 10. RESUMO FINAL
        print("\n" + "="*70)
        print("RESUMO FINAL")
        print("="*70)

        in_consistente = in_matches == total_validas
        out_consistente = out_matches == total_validas
        totalmente_consistente = in_consistente and out_consistente

        if totalmente_consistente:
            print("✅ TOTALMENTE CONSISTENTE")
            print(f"   Todos os {total_validas:,} in_degrees e out_degrees batem perfeitamente!")
        else:
            print("❌ INCONSISTÊNCIAS DETECTADAS")
            
            if not in_consistente:
                print(f"   • IN-DEGREE: {total_validas - in_matches:,} diferenças ({(total_validas - in_matches)/total_validas*100:.2f}%)")
            else:
                print(f"   ✅ IN-DEGREE: Todos consistentes")
            
            if not out_consistente:
                print(f"   • OUT-DEGREE: {total_validas - out_matches:,} diferenças ({(total_validas - out_matches)/total_validas*100:.2f}%)")
            else:
                print(f"   ✅ OUT-DEGREE: Todos consistentes")
            
            print(f"\n   Possíveis causas:")
            print(f"   - Timestep usado pode não ser o correto")
            print(f"   - Features podem incluir edges temporários/removidos")
            print(f"   - Edges duplicadas nas edgelists")
            print(f"   - Cálculo de features pode usar critério diferente")

        # 11. Salvar diferenças para análise
        if not totalmente_consistente:
            print("\n11. SALVANDO DIFERENÇAS PARA ANÁLISE")
            
            diferencas_completas = comparacao_valida[
                ~comparacao_valida['in_degree_match'] | 
                ~comparacao_valida['out_degree_match']
            ].copy()
            
            diferencas_completas['in_diff'] = (
                diferencas_completas['in_degree_features'] - diferencas_completas['in_degree_real']
            )
            diferencas_completas['out_diff'] = (
                diferencas_completas['out_degree_features'] - diferencas_completas['out_degree_real']
            )
            
            output_path = 'data/analise/diferencas_degrees.parquet'
            diferencas_completas.to_parquet(output_path, index=False)
            print(f"✓ Salvo: {output_path} ({len(diferencas_completas):,} registros)")
        
        return self

    def run(self):
        # Implement validation logic here
        print(f"Running validations on data in {self.path}...\n\n")
        self.validate_wallets_features_classes_combined()
        self.validate_addraddr_edgelist()
        self.validate_illicit_transactions_with_addresses()
        self.validate_transaction_degrees()