
import json


class ResultCollectingAgent():
    def __init__(self, input_result_directory: str, output_result_directory: str):
        self.input_result_directory = input_result_directory
        # self.dataset_directory = dataset_directory
        self.output_result_directory = output_result_directory

    def process(self):
        with open(self.input_result_directory, 'r', encoding='utf-8') as f:
            data = json.load(f)
            for input_json in data:
                output_json = [
                    {
                        "node_type": "candidate_generation",
                        "question_id": input_json["question_id"],
                        "db_id": input_json["db_id"],
                        "question": input_json["question"],
                        "GOLD_SQL": input_json["SQL"],
                        "PREDICTED_SQL": input_json["possible_sql"],
                        "prompt_tokens": input_json["candidate_sql_generation"]["prompt_tokens"],
                        "completion_tokens": input_json["candidate_sql_generation"]["completion_tokens"],
                        "total_tokens": input_json["candidate_sql_generation"]["total_tokens"],
                    },
                    {
                        "node_type": "revision",
                        "question_id": input_json["question_id"],
                        "db_id": input_json["db_id"],
                        "question": input_json["question"],
                        "enriched_question": input_json["question_enrichment"]["enriched_question"],
                        "GOLD_SQL": input_json["SQL"],
                        "PREDICTED_SQL": input_json["predicted_sql"],
                        "prompt_tokens": input_json["question_enrichment"]["prompt_tokens"] + input_json["sql_refinement"]["prompt_tokens"],
                        "completion_tokens": input_json["question_enrichment"]["completion_tokens"] + input_json["sql_refinement"]["completion_tokens"],
                        "total_tokens": input_json["question_enrichment"]["total_tokens"] + input_json["sql_refinement"]["total_tokens"],
                    }
                ]
                print("Prociessing question_id:",
                      input_json["question_id"], "db_id:", input_json["db_id"])
                output_file = f"{self.output_result_directory}/{input_json['question_id']}_{input_json['db_id']}.json"
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(output_json, f, ensure_ascii=False, indent=4)


def main():
    input_result_directory = "./results/model_outputs_dev_CSG-QE-SR_deepseek-chat/predictions.json"
    output_result_directory = "./results/e_on_bird_dev_deepseek/bird_dev_deepseek_v3"
    result_collecting_agent = ResultCollectingAgent(
        input_result_directory, output_result_directory)
    result_collecting_agent.process()


if __name__ == "__main__":
    main()
