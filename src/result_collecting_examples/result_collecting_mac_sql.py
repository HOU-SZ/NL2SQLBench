
import json
import sqlite3


class ResultCollectingAgent():
    def __init__(self, input_result_directory: str, dataset_directory: str, output_result_directory: str):
        self.input_result_directory = input_result_directory
        self.dataset_directory = dataset_directory
        self.output_result_directory = output_result_directory

    def _get_table_columns(self, dataset_directory: str, db_id: str, table_name: str):
        db_path = f"{dataset_directory}/{db_id}/{db_id}.sqlite"
        print(f"db_path: {db_path}")
        conn = sqlite3.connect(db_path)
        # avoid gbk/utf8 error, copied from sql-eval.exec_eval
        conn.text_factory = lambda b: b.decode(errors="ignore")
        cursor = conn.cursor()
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        columns = [column[1] for column in columns]
        cursor.close()
        conn.close()
        return columns

    def process(self):
        with open(self.input_result_directory, 'r', encoding='utf-8') as f:
            data = []
            for line in f:
                # 跳过空行
                if line.strip():
                    try:
                        # 将每行解析为 JSON 对象并添加到列表
                        data.append(json.loads(line.strip()))
                    except json.JSONDecodeError as e:
                        print(f"解析错误: {e}，行内容: {line.strip()}")
            for input_json in data:
                final_schema = input_json['chosen_db_schem_dict']
                output_json = [
                    {
                        "node_type": "schema_extraction",
                        "question_id": input_json["idx"],
                        "db_id": input_json["db_id"],
                        "question": input_json["query"],
                        "extracted_schema": final_schema,
                        "prompt_tokens": input_json["selector_token_and_time"]["prompt_tokens"] if "selector_token_and_time" in input_json else 0,
                        "completion_tokens": input_json["selector_token_and_time"]["completion_tokens"] if "selector_token_and_time" in input_json else 0,
                        "total_tokens": input_json["selector_token_and_time"]["total_tokens"] if "selector_token_and_time" in input_json else 0,
                        "llm_time": input_json["selector_token_and_time"]["llm_time"] if "selector_token_and_time" in input_json else 0,
                    },
                    {
                        "node_type": "candidate_generation",
                        "question_id": input_json["idx"],
                        "db_id": input_json["db_id"],
                        "question": input_json["query"],
                        "GOLD_SQL": input_json["ground_truth"],
                        "PREDICTED_SQL": input_json["final_sql"],
                        "prompt_tokens": input_json["decomposer_token_and_time"]["prompt_tokens"],
                        "completion_tokens": input_json["decomposer_token_and_time"]["completion_tokens"],
                        "total_tokens": input_json["decomposer_token_and_time"]["total_tokens"],
                        "llm_time": input_json["decomposer_token_and_time"]["llm_time"],
                    },
                    {
                        "node_type": "revision",
                        "question_id": input_json["idx"],
                        "db_id": input_json["db_id"],
                        "question": input_json["query"],
                        "GOLD_SQL": input_json["ground_truth"],
                        "PREDICTED_SQL": input_json["pred"],
                        "prompt_tokens": input_json["refiner_token_and_time"]["prompt_tokens"] if "refiner_token_and_time" in input_json else 0,
                        "completion_tokens": input_json["refiner_token_and_time"]["completion_tokens"] if "refiner_token_and_time" in input_json else 0,
                        "total_tokens": input_json["refiner_token_and_time"]["total_tokens"] if "refiner_token_and_time" in input_json else 0,
                        "llm_time": input_json["refiner_token_and_time"]["llm_time"] if "refiner_token_and_time" in input_json else 0,
                    }
                ]
                output_file = f"{self.output_result_directory}/{input_json['idx']}_{input_json['db_id']}.json"
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(output_json, f, ensure_ascii=False, indent=4)

    def evaluation(self):
        pass


def main():
    input_result_directory = "./outputs/bird_dev_deepseek_v3_3/output_bird_dev.json"
    dataset_directory = "./data/dev_20240627/dev_databases"
    output_result_directory = "./results/mac_on_bird_dev_deepseek/bird_dev_deepseek_v3"
    result_collecting_agent = ResultCollectingAgent(
        input_result_directory, dataset_directory, output_result_directory)
    result_collecting_agent.process()


if __name__ == "__main__":
    main()
