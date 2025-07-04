import json
import os


class ResultCollectingAgent():
    def __init__(self, input_result_directory: str, output_result_directory: str):
        self.input_result_directory = input_result_directory
        # self.dataset_directory = dataset_directory
        self.output_result_directory = output_result_directory

    def process(self):
        for file in os.listdir(self.input_result_directory):
            if "_" not in file or "predict_dev" in file:
                continue
            if file.endswith(".json") and "_" in file:
                print(file)
                _index = file.find("_")
                question_id = int(file[:_index])
                db_id = file[_index + 1:-5]
                with open(os.path.join(self.input_result_directory, file), "r", encoding="utf-8") as f:
                    result = json.load(f)
                    # schema_extraction_prompt_tokens = 0
                    # schema_extraction_completion_tokens = 0
                    # schema_extraction_total_tokens = 0
                    # schema_extraction_call_llm_times = 0
                    candidate_generation_prompt_tokens = 0
                    candidate_generation_completion_tokens = 0
                    candidate_generation_total_tokens = 0
                    candidate_generation_call_llm_times = 0
                    revision_prompt_tokens = 0
                    revision_completion_tokens = 0
                    revision_total_tokens = 0
                    revision_call_llm_times = 0
                    for step in result:
                        if "tool_name" in step and (step["tool_name"] in ["generate_candidate", "extract_keywords"]):
                            candidate_generation_prompt_tokens += step.get(
                                "prompt_tokens", 0)
                            candidate_generation_completion_tokens += step.get(
                                "completion_tokens", 0)
                            candidate_generation_total_tokens += step.get(
                                "total_tokens", 0)
                            candidate_generation_call_llm_times += step.get(
                                "call_llm_times", 0)
                            if step["tool_name"] == "generate_candidate":
                                predicted_sql_candidate = [
                                    ele["SQL"] for ele in step["candidates"]]
                        elif "tool_name" in step and step["tool_name"] in ["revise", "generate_unit_test", "evaluate"]:
                            revision_prompt_tokens += step.get(
                                "prompt_tokens", 0)
                            revision_completion_tokens += step.get(
                                "completion_tokens", 0)
                            revision_total_tokens += step.get(
                                "total_tokens", 0)
                            revision_call_llm_times += step.get(
                                "call_llm_times", 0)
                            if step["tool_name"] == "evaluate":
                                predicted_sql_revision = step.get(
                                    "PREDICTED_SQL", "")
                    output_json = [
                        {
                            "node_type": "candidate_generation",
                            "question_id": question_id,
                            "db_id": db_id,
                            "PREDICTED_SQL": predicted_sql_candidate,
                            "prompt_tokens": candidate_generation_prompt_tokens,
                            "completion_tokens": candidate_generation_completion_tokens,
                            "total_tokens": candidate_generation_total_tokens,
                            "call_llm_times": candidate_generation_call_llm_times,
                        },
                        {
                            "node_type": "revision",
                            "question_id": question_id,
                            "db_id": db_id,
                            "PREDICTED_SQL": predicted_sql_revision,
                            "prompt_tokens": revision_prompt_tokens,
                            "completion_tokens": revision_completion_tokens,
                            "total_tokens": revision_total_tokens,
                            "call_llm_times": revision_call_llm_times,
                        }
                    ]
                    print("Prociessing question_id:",
                          question_id, "db_id:", db_id)
                output_file = f"{self.output_result_directory}/{output_json['question_id']}_{output_json['db_id']}.json"
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(output_json, f, ensure_ascii=False, indent=4)


def main():
    input_result_directory = "./results/chess_v2_on_bird_dev_deepseek/original_results"
    output_result_directory = "./results/chess_v2_on_bird_dev_deepseek/bird_dev_deepseek_v3"
    result_collecting_agent = ResultCollectingAgent(
        input_result_directory, output_result_directory)
    result_collecting_agent.process()


if __name__ == "__main__":
    main()
