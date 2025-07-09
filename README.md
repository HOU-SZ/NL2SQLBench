# NL2SQLBench: A Modular Benchmarking Framework for LLM-Enabled NL2SQL Solutions
This is the official repository for the paper **"NL2SQLBench: A Modular Benchmarking Framework for LLM-Enabled NL2SQL Solutions"**
<p align="center">
<img width="800" src="./static/images/evaluation_framework.jpg"/>
</p>

## 🔍 Overview

Natural Language to SQL (NL2SQL) technology empowers non-expert users to query relational databases without requiring SQL expertise. While large language models (LLMs) have greatly improved NL2SQL algorithms, their rapid development outpaces systematic evaluation, leaving a critical gap in understanding their effectiveness, efficiency, and limitations. 

To this end, we present **NL2SQLBench**, the first modular evaluation and benchmarking framework for LLM-enabled NL2SQL approaches. Specifically, we dissect NL2SQL systems into three core modules: **Schema Selection**, **Candidate Generation**, and **Query Revision**. For each module, we comprehensively review existing strategies and propose novel **fine-grained metrics** that systematically quantify module-level effectiveness and efficiency. We further implement these metrics in a flexible multi-agent benchmarking framework consisting of three agents: Result Collecting, Result Postprocessing, and Benchmarking agent, allowing configurable benchmarking across diverse NL2SQL approaches. Leveraging **NL2SQLBench**, we rigorously evaluate ten representative open-source methods from the BIRD leaderboard on its widely adopted development dataset. We systematically assess each approach across the three core modules and evaluate multiple critical performance dimensions. 

## ⚙️ Framework Architecture

- **Result Collecting Agent**: This agent collects the results required for evaluation metrics from each module. It gathers selected schemas, candidate SQL queries, and refined SQL queries from the Schema Selection, Candidate Generation, and Query Revision modules, respectively. It also collects LLM usage statistics, such as token costs and the number of LLM calls. All the collected information is consolidated into structured JSON files

    For each question, an example format of the JSON file is shown as below:
    ```json
    [  
        {
            "node_type": "schema_selection",
            "question_id": 372,
            "db_id": "card_games",
            "question": "How many cards are there with toughness of 99?",
            "extracted_schema": { "cards": ["id", "toughness"] }
            "prompt_tokens": 9396,
            "completion_tokens": 238,
            "total_tokens": 9634,
            "call_llm_times": 1
        },
        {
            "node_type": "candidate_generation",
            "question_id": 372,
            "db_id": "card_games",
            "question": "How many cards are there with toughness of 99?",
            "PREDICTED_SQL": "SELECT COUNT(id) FROM cards WHERE toughness = 99",
            "GOLD_SQL": "SELECT COUNT(id) FROM cards WHERE toughness = 99",
            "prompt_tokens": 9396,
            "completion_tokens": 238,
            "total_tokens": 9634,
            "call_llm_times": 1
        },
        {
            "node_type": "query_revision",
            "question_id": 372,
            "db_id": "card_games",
            "question": "How many cards are there with toughness of 99?",
            "PREDICTED_SQL": "SELECT COUNT(id) FROM cards WHERE toughness = 99",
            "GOLD_SQL": "SELECT COUNT(id) FROM cards WHERE toughness = 99",
            "prompt_tokens": 9396,
            "completion_tokens": 238,
            "total_tokens": 9634,
            "call_llm_times": 1
        }
    ]
    ```
- **Postprocessing Agent**: This agent is responsible for transforming the raw outputs collected from upstream modules into a standardized and structured format suitable for downstream benchmarking. The core responsibilities of this agent are summarized below.
    - Gold Schema Extraction: Parse gold SQL queries to extract schema elements such as involved tables and columns. These components are then annotated as the gold schema, serving as the reference for assessing schema selection accuracy.
    - SQL Execution and Evaluation. Execute both the candidate and the refined SQL queries on the target database and compare their execution results with those of the gold SQL to determine execution correctness and identify errors. All evaluation outputs—including correctness labels, error categories, and associated metadata—are serialized into structured JSON files for downstream analysis.
    - Statistical Analysis. In addition to execution-based evaluation, the agent compiles detailed performance statistics, which include the total number of executed queries, success and failure counts, as well as per-question result summaries.

    For each question, the extracted gold schema and SQL execution and evaluation results are outputed into a JSON file is shown as below:
    ```json
    [  
        {
            "node_type": "schema_selection",
            "question_id": 372,
            "db_id": "card_games",
            "question": "How many cards are there with toughness of 99?",
            "extracted_schema": { "cards": ["id", "toughness"] },
            "real_schema": { "cards": ["id", "toughness"] },
            "prompt_tokens": 9396,
            "completion_tokens": 238,
            "total_tokens": 9634,
            "call_llm_times": 1
        },
        {
            "node_type": "candidate_generation",
            "question_id": 372,
            "db_id": "card_games",
            "question": "How many cards are there with toughness of 99?",
            "PREDICTED_SQL": "SELECT COUNT(id) FROM cards WHERE toughness = 99",
            "GOLD_SQL": "SELECT COUNT(id) FROM cards WHERE toughness = 99",
            "prompt_tokens": 9396,
            "completion_tokens": 238,
            "total_tokens": 9634,
            "call_llm_times": 1
        },
        {
            "node_type": "query_revision",
            "question_id": 372,
            "db_id": "card_games",
            "question": "How many cards are there with toughness of 99?",
            "PREDICTED_SQL": "SELECT COUNT(id) FROM cards WHERE toughness = 99",
            "GOLD_SQL": "SELECT COUNT(id) FROM cards WHERE toughness = 99",
            "prompt_tokens": 9396,
            "completion_tokens": 238,
            "total_tokens": 9634,
            "call_llm_times": 1
        },
        {
            "node_type": "evaluation",
            "candidate_generation": {
                "question_id": 372,
                "db_id": "card_games",
                "question": "How many cards are there with toughness of 99?",
                "GOLD_SQL": "SELECT COUNT(id) FROM cards WHERE toughness = 99",
                "PREDICTED_SQL": "SELECT COUNT(id) FROM cards WHERE toughness = 99",
                "exec_res": 1,
                "exec_err": "--",
            },
            "query_revision": {
                "question_id": 372,
                "db_id": "card_games",
                "question": "How many cards are there with toughness of 99?",
                "GOLD_SQL": "SELECT COUNT(id) FROM cards WHERE toughness = 99",
                "PREDICTED_SQL": "SELECT COUNT(id) FROM cards WHERE toughness = 99",
                "exec_res": 1,
                "exec_err": "--",
            },
            "status": "success"
        }
    ]
    ```
    The statistical analysis result are shown as below:
    ```json
    {
        "counts": {
            "candidate_generation": {
                "correct": 914,
                "incorrect": 545,
                "error": 75,
                "total": 1534
            },
            "query_revision": {
                "correct": 920,
                "incorrect": 525,
                "error": 89,
                "total": 1534
            }
        },
        "ids": {
            "candidate_generation": {
                "correct": [...],
                "incorrect": [...],
                "error": [...],
            },
            "query_revision": {
                "correct": [...],
                "incorrect": [...],
                "error": [...],
            }
        },
    }
    ```
- **Benchmarking Agent**: Utilizing the processed datasets, this agent performs a comprehensive and modular evaluation of each module within an NL2SQL solution. Specifically, it leverages the previously defined evaluation metrics and formalized equations to compute quantitative performance indicators for each module, including Schema Selection, Candidate Generation, and Query Revision. For each module, the agent aggregates relevant statistics and analyzes these metrics across varying difficulty levels of questions, enabling a granular assessment.

    The benchmarking agent outputs the evaluation results in a structured JSON format. Please see the `results` directory for examples of the evaluation results.

## 💡 Project Outline

```text
├─data/
│  └─bird/
│      └─dev/
│          ├─dev_databases/
│          ├─dev.sql
│          ├dev.json
│          ├dev_tied_append.json
│          ├dev_tables.json
│       
│             
├─results/
│  ├─chess_on_dev/
│  ├─e_on_bird_dev_deepseek/
│  ├─mac_on_bird_dev_deepseek/
│  └─...
│
├─src/
│  ├─database_utils/
│  │  └─execution.py
│  ├─result_collecting_examples/
│  │   └─...
│  ├─runner/
│  ├   └─statistics_manager.py
│  ├─postprocessing.py
│  ├─benchmarking.py
│  └─utils.py
│
└─static/
    └─images
```

## 🚀 Run
To run the benchmarking get the evaluation results
1. Download the BIRD dev set into ./data/bird/dev/
2. Rerun the approaches to evaluated (need to config the coressponding LLMs, datasets, and change necessary codes) and the result collecting agent to collect the results. The result files should be placed in the `./results/` directory.
3. Run the postprocessing agent to process the results and generate the evaluation files.
4. Run the benchmarking agent to evaluate the results and generate the final evaluation files.

## 📊 Evaluation Results
- Dataset: We evaluate the NL2SQL approaches on the **BIRD dev set**, which is a widely adopted benchmark for NL2SQL tasks. The BIRD dev set contains 1534 questions across 11 databases, covering a wide range of SQL queries and database schemas.
- Approaches: We choose a list of representative and open-sourced approaches from the BIRD leaderboard: C3-SQL, DIN-SQL, MAC-SQL, TA-SQL, CHESS(IR,SS,CG), CHESS(IR,CG,UT), E-SQL, RSL-SQL, OpenSearch-SQL and GSR. These approaches cover diverse strategies for the three core modules of NL2SQL (Fine-tuned or RL-trained models will be evaluated in the future).
- Language Model: To ensure a fair and consistent comparison across all approaches while minimizing the experimental costs, we utilize **DeepSeek-V3** (We use the DeepSeek-V3-0324 Release version) as the unified LLM for all evaluations. For model-related hyperparameters such as temperature, maximum tokens, and prompt settings, we retain the original configurations used by each evaluated method to ensure fairness and objectivity in evaluation. For the approaches that require models for embedding and retrieval, we choose the model `bge-large-en-v1.5`.
- Evaluation Results: The evaluation results are stored in the `./results/` directory. Each subdirectory corresponds to a specific NL2SQL approach and contains the evaluation results for the BIRD dev set. The results include detailed statistics and performance metrics for each module of the NL2SQL solutions.


## 🙌 Contribution
We welcome contributions to NL2SQLBench! If you have suggestions for improvements, bug fixes, or new features, please open an issue or submit a pull request.