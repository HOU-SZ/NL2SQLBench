import json
import os
from pathlib import Path
import random
import re

DB_ROOT_PATH = "./data/dev"
db_mode = "dev"


class ResultCollectingAgent():
    def __init__(self, input_result_directory: str, output_result_directory: str, real_schema_directory: str, multiple_candidate: bool, pass_at_k: str):
        self.input_result_directory = input_result_directory
        # self.dataset_directory = dataset_directory
        self.output_result_directory = output_result_directory

    def sql_raw_parse(self, sql):
        sql = sql.split('/*')[0].strip().replace('```sql',
                                                 '').replace('```', '')
        sql = re.sub("```.*?", '', sql)
        sql = sql.split('#SQL:')[-1]
        if sql.startswith("\"") or sql.startswith("\'"):  # 消除"SELECT
            sql = sql[1:-1]
        sql = re.sub('\s+', ' ', sql).strip()
        return sql

    def preprocess(self):
        for file in os.listdir(self.input_result_directory):
            if "_" not in file or "predict_dev" in file:
                continue
            if file.endswith(".json") and "_" in file:
                _index = file.find("_")
                question_id = int(file[:_index])
                db_id = file[_index + 1:-5]
                with open(os.path.join(self.input_result_directory, file), "r", encoding="utf-8") as f:
                    result = json.load(f)
                node_type_map = {
                    "generate_db_schema": "schema_extraction",
                    "extract_col_value": "schema_extraction",
                    "extract_query_noun": "schema_extraction",
                    "column_retrieve_and_other_info": "schema_extraction",
                    "candidate_generate": "candidate_generation",
                    "align_correct": "revision",
                    "vote": "revision",
                    "evaluation": "evaluation",
                }
                schema_extraction = {
                    "node_type": "schema_extraction",
                    "question_id": question_id,
                    "db_id": db_id,
                    "prompt_tokens": 0,
                    "completion_tokens": 0,
                    "total_tokens": 0,
                    "prompt_cache_hit_tokens": 0,
                    "prompt_cache_miss_tokens": 0,
                    "llm_time": 0,
                    "call_llm_times": 0,
                }
                candidate_generation = {
                    "node_type": "candidate_generation",
                    "question_id": question_id,
                    "db_id": db_id,
                    "prompt_tokens": 0,
                    "completion_tokens": 0,
                    "total_tokens": 0,
                    "prompt_cache_hit_tokens": 0,
                    "prompt_cache_miss_tokens": 0,
                    "llm_time": 0,
                    "call_llm_times": 0,
                }
                align_correct = {
                    "node_type": "align_correct",
                    "question_id": question_id,
                    "db_id": db_id,
                }
                revision = {
                    "node_type": "revision",
                    "question_id": question_id,
                    "db_id": db_id,
                    "prompt_tokens": 0,
                    "completion_tokens": 0,
                    "total_tokens": 0,
                    "prompt_cache_hit_tokens": 0,
                    "prompt_cache_miss_tokens": 0,
                    "llm_time": 0,
                    "call_llm_times": 0,
                }
                evaluation = {
                    "node_type": "evaluation",
                }
                for step in result:
                    if node_type_map[step["node_type"]] == "schema_extraction":
                        schema_extraction["prompt_tokens"] += step.get(
                            "prompt_tokens", 0)
                        schema_extraction["completion_tokens"] += step.get(
                            "completion_tokens", 0)
                        schema_extraction["total_tokens"] += step.get(
                            "total_tokens", 0)
                        schema_extraction["prompt_cache_hit_tokens"] += step.get(
                            "prompt_cache_hit_tokens", 0)
                        schema_extraction["prompt_cache_miss_tokens"] += step.get(
                            "prompt_cache_miss_tokens", 0)
                        schema_extraction["llm_time"] += step.get(
                            "llm_time", 0)
                        schema_extraction["call_llm_times"] += step.get(
                            "call_llm_times", 0)
                    if node_type_map[step["node_type"]] == "candidate_generation" and "token_and_time_cost" in step:
                        for item in step["token_and_time_cost"]:
                            candidate_generation["prompt_tokens"] += item.get(
                                "prompt_tokens", 0)
                            candidate_generation["completion_tokens"] += item.get(
                                "completion_tokens", 0)
                            candidate_generation["total_tokens"] += item.get(
                                "total_tokens", 0)
                            candidate_generation["prompt_cache_hit_tokens"] += item.get(
                                "prompt_cache_hit_tokens", 0)
                            candidate_generation["prompt_cache_miss_tokens"] += item.get(
                                "prompt_cache_miss_tokens", 0)
                            candidate_generation["llm_time"] += item.get(
                                "llm_time", 0)
                            candidate_generation["call_llm_times"] += item.get(
                                "call_llm_times", 0)
                    if node_type_map[step["node_type"]] == "revision":
                        if step["node_type"] == "align_correct" and "vote" in step:
                            for item in step["vote"]:
                                if item["token_and_time_cost"] != {}:
                                    revision["prompt_tokens"] += item["token_and_time_cost"]["prompt_tokens"]
                                    revision["completion_tokens"] += item["token_and_time_cost"]["completion_tokens"]
                                    revision["total_tokens"] += item["token_and_time_cost"]["total_tokens"]
                                    revision["prompt_cache_hit_tokens"] += item["token_and_time_cost"]["prompt_cache_hit_tokens"]
                                    revision["prompt_cache_miss_tokens"] += item["token_and_time_cost"]["prompt_cache_miss_tokens"]
                                    revision["llm_time"] += item["token_and_time_cost"]["llm_time"]
                                    revision["call_llm_times"] += item["token_and_time_cost"]["call_llm_times"]
                    if step["node_type"] == "column_retrieve_and_other_info":
                        schema_extraction["extracted_schema"] = step.get(
                            "selected_columns", {})
                    if step["node_type"] == "candidate_generate":
                        sqls = step.get("SQL", [])
                        sqls_parsed = [self.sql_raw_parse(sql) for sql in sqls]
                        candidate_generation["PREDICTED_SQL"] = sqls_parsed
                    if step["node_type"] == "vote":
                        revision["PREDICTED_SQL"] = step.get("SQL", "--")
                    if step["node_type"] == "evaluation":
                        candidate_generation["GOLD_SQL"] = step["candidate_generate"]["GOLD_SQL"]
                        candidate_generation["exec_res"] = step["candidate_generate"]["exec_res"]
                        candidate_generation["exec_err"] = step["candidate_generate"]["exec_err"]
                        align_correct["PREDICTED_SQL"] = step["align_correct"]["PREDICTED_SQL"]
                        align_correct["GOLD_SQL"] = step["align_correct"]["GOLD_SQL"]
                        align_correct["exec_res"] = step["align_correct"]["exec_res"]
                        align_correct["exec_err"] = step["align_correct"]["exec_err"]
                        revision["GOLD_SQL"] = step["vote"]["GOLD_SQL"]
                        revision["exec_res"] = step["vote"]["exec_res"]
                        revision["exec_err"] = step["vote"]["exec_err"]

                        evaluation["candidate_generation"] = step["candidate_generate"]
                        evaluation["revision"] = step["vote"]
                        evaluation["status"] = step["status"]
                # print(result)
                output = [schema_extraction,
                          candidate_generation, align_correct, revision, evaluation]
                # write the updated result to the original file
                with open(os.path.join(self.input_result_directory+"_pass_at_1", file), "w", encoding="utf-8") as f:
                    json.dump(output, f, indent=4)


def main():
    input_result_directory = "./results/opensearch_on_bird_dev_deepseek/original_results"
    output_result_directory = "./results/opensearch_on_bird_dev_deepseek/bird_dev_deepseek_v3"
    result_collecting_agent = ResultCollectingAgent(
        input_result_directory, output_result_directory)
    result_collecting_agent.process()


if __name__ == "__main__":
    main()
