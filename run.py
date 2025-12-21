from src.main import main

def run():
    main()

if __name__ == "__main__":
    run()

'''
- [Done] Extração dos CSVs do drive do malandro (ou do meu drive)
- Transformação dos CSVs -> selecionar quais colunas necessárias para cada tabela
- Extração agregada -> jogar todos as colunas que vou precisar + a classificação em um csv/parquet puro
	- Verificar se vou precisar fazer sampling dos dados por conta de performance
	- Verificar se vou precisar subir os dados em algum banco de dados
	- Verificar se vou precisar usar spark
'''