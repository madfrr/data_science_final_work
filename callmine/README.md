
# CallMine  

**CallMine: Fraud Detection and Visualization of Million-Scale Call Graphs**  


**Authors:** Mirela Cazzolato<sup>1,2</sup>, Saranya Vijayakumar<sup>1</sup>, Meng-Chieh Lee<sup>1</sup>, Catalina Vajiac<sup>1</sup>, Namyong Park<sup>1</sup>, Pedro Fidalgo<sup>3,4</sup>,  Agma J. M. Traina<sup>2</sup>, Christos Faloutsos<sup>1</sup>  

**Affiliations:**  <sup>1</sup> Carnegie Mellon University (CMU), <sup>2</sup> University of São Paulo (USP), <sup>3</sup> Mobileum, <sup>4</sup> ISCTE-IUL  

*Work accepted for publication at CIKM'2023*

## Setup environment  

To create and use a virtual environment, type: 
- `python -m venv wcw_venv`
- `source wcw_venv/bin/activate`

To install the requirements:

 - `pip install -r requirements.txt` or simply `make prep`

## Usage:  

Type `make demo` to see a demo of CallMine and CallMine-Focus  

## Docker
```
docker build -t callmine-demo .

docker run --rm -v $(pwd):/app -e OUTPUT_DIR=/app/data callmine-demo
docker run --rm -v $(pwd)/outputs:/app/outputs callmine-demo

```

```bash
brew install pyenv uv
pyenv install 3.10.19
pyenv local 3.10.19   # cria .python-version

uv venv
source .venv/bin/activate
uv pip install pandas numpy
```

```bash
brew install --cask miniconda
conda create -n myenv python=3.10.19
conda activate myenv

which python
python --version
pip --version
pip install -r requirements.txt
```

python3 tgraph/static_graph.py -v -v INPUT_DATA/sample_raw_data.csv
python3 tgraph/temporal_graph.py -v -v INPUT_DATA/sample_raw_data.csv
python3 tgraph/join_feature_files.py -v nodeVectors.csv t_nodeVectors.csv
python3 callmine_focus/run_callmine_focus.py allFeatures_nodeVectors.csv 1 10 5 2 "outputs/"
python3 callmine_focus/run_callmine_focus.py allFeatures_nodeVectors.csv 1 10 5 3 "outputs/"



### Sample Dataset:  

File `INPUT_DATA/sample_raw_data.csv'` has a synthetic data sample with:  

11,000 calls, consisting of
 - 10,000 random calls:  
	 - 2,000 sources  
	 - 2,000 destinations  
	 - 5 days  
- Cluster with 1,000 calls 
	- 10 sources  
	- 10 destinations  
	- Phone calls with duration between 20 and 40 seconds  
