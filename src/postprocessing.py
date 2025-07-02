import json
import os
from pathlib import Path
import random

# from runner.database_manager import DatabaseManager
from database_utils.execution import compare_sqls
from runner.statistics_manager import StatisticsManager

DB_ROOT_PATH = "./data/bird/dev"
db_mode = "dev"


class PostprocessingAgent():
    def __init__(self, input_result_directory, dataset_directory, output_result_directory, real_schema_directory, multiple_candidate, pass_at_k="pass_at_1"):
        """
        Initializes the PostprocessingAgent.
        Args:
            input_result_directory (str): Directory containing the input results.
            dataset_directory (str): Directory containing the dataset.
            output_result_directory (str): Directory to save the output results.
            real_schema_directory (str): Directory containing the real schema files.
            multiple_candidate (bool): Whether to handle multiple candidate SQLs.
            pass_at_k (str): The pass@k metric to use for evaluation.
        """
        self.input_result_directory = input_result_directory
        self.dataset_directory = dataset_directory
        self.output_result_directory = output_result_directory
        self.real_schema_directory = real_schema_directory
        self.pass_at_k = pass_at_k
        self.multiple_candidate = multiple_candidate
        if multiple_candidate:
            self.statistics_manager = StatisticsManager(
                self.input_result_directory+"_"+self.pass_at_k)
        else:
            self.statistics_manager = StatisticsManager(
                self.input_result_directory)
        self.pass_at_k_dict = {
            "pass_at_1": 1,
            "pass_at_5": 5,
            "pass_at_10": 10,
            "pass_at_15": 15,
            "pass_at_20": 20
        }

    def preprocess(self):
        """ Preprocesses the input results to add real schema information.
        This method updates the result files in the input result directory by adding the real schema information
        to the schema extraction steps. It matches the result files with the corresponding real schema files based
        on the question ID and database ID.
        """
        for file in os.listdir(self.input_result_directory):
            if "_" not in file or "predict_dev" in file:
                continue
            if file.endswith(".json") and "_" in file:
                _index = file.find("_")
                question_id = int(file[:_index])
                db_id = file[_index + 1:-5]
                for file_2 in os.listdir(self.real_schema_directory):
                    if file_2.endswith(".json") and file_2.startswith(db_id):
                        _index_2 = [i for i in range(
                            len(file_2)) if file_2[i] == "_"][-1]
                        question_id_2 = int(file_2[_index_2 + 1:-5])
                        if question_id_2 == question_id:
                            print(file, file_2)
                            real_schema_file = file_2
                            break
                with open(os.path.join(self.input_result_directory, file), "r", encoding="utf-8") as f:
                    result = json.load(f)
                with open(os.path.join(self.real_schema_directory, real_schema_file), "r", encoding="utf-8") as f:
                    real_schema = json.load(f)
                for step in result:
                    if step["node_type"] == "schema_extraction":
                        for step_2 in real_schema:
                            if step_2["node_type"] == "column_selection" or step_2["node_type"] == "table_selection":
                                step["real_schema"] = step_2["correct_columns"]
                                break
                        break
                # write the updated result to the original file
                with open(os.path.join(self.input_result_directory, file), "w", encoding="utf-8") as f:
                    json.dump(result, f, indent=4)

    def evaluate(self):
        """ Evaluates the SQL predictions against the ground truth.
        This method compares the predicted SQLs with the ground truth SQLs for each question in the input result directory.
        It checks the execution results and errors, and updates the evaluation node with the results.
        The results are saved back to the original files in the input result directory or a modified directory based on the pass_at_k metric.
        """
        print("start evaluation")
        if self.multiple_candidate:
            output_directory = self.input_result_directory+"_"+self.pass_at_k
        else:
            output_directory = self.input_result_directory
        for file in os.listdir(self.input_result_directory):
            if "_" not in file or "predict_dev" in file:
                continue
            if file.endswith(".json") and "_" in file:
                print(file)
                _index = file.find("_")
                question_id = int(file[:_index])
                db_id = file[_index + 1:-5]
                db_path = Path(DB_ROOT_PATH) / \
                    f"{db_mode}_databases" / db_id / f"{db_id}.sqlite"
                with open(os.path.join(self.input_result_directory, file), "r", encoding="utf-8") as f:
                    result = json.load(f)
                    evaluation_node = {"node_type": "evaluation",
                                       "candidate_generation": {}, "revision": {}}
                    for node in result:
                        if node["node_type"] == "candidate_generation":
                            ground_truth_sql = node["GOLD_SQL"]
                            if isinstance(node["PREDICTED_SQL"], list):
                                if self.pass_at_k == "pass_at_1":
                                    predicted_sql = node["PREDICTED_SQL"][0]
                                else:
                                    for i in range(self.pass_at_k_dict[self.pass_at_k]):
                                        if len(node["PREDICTED_SQL"]) == 0:
                                            predicted_sql = "--"
                                            break
                                        if i == self.pass_at_k_dict[self.pass_at_k] - 1:
                                            predicted_sql = node["PREDICTED_SQL"][i]
                                            break
                                        else:
                                            predicted_sql = node["PREDICTED_SQL"][i]
                                            if compare_sqls(
                                                db_path=str(db_path),
                                                predicted_sql=predicted_sql,
                                                ground_truth_sql=ground_truth_sql,
                                            )["exec_res"] == 1:
                                                break
                            else:
                                predicted_sql = node["PREDICTED_SQL"]
                            response = compare_sqls(
                                db_path=str(db_path),
                                predicted_sql=predicted_sql,
                                ground_truth_sql=ground_truth_sql,
                            )
                            node["exec_res"] = response["exec_res"]
                            node["exec_err"] = response["exec_err"]
                            evaluation_node["candidate_generation"]["exec_res"] = node["exec_res"]
                            evaluation_node["candidate_generation"]["exec_err"] = node["exec_err"]
                            evaluation_node["candidate_generation"]["question_id"] = question_id
                            evaluation_node["candidate_generation"]["db_id"] = db_id
                            evaluation_node["candidate_generation"]["question"] = node.get(
                                "question", "")
                            evaluation_node["candidate_generation"]["GOLD_SQL"] = ground_truth_sql
                            evaluation_node["candidate_generation"]["PREDICTED_SQL"] = predicted_sql
                        if node["node_type"] == "revision":
                            ground_truth_sql = node["GOLD_SQL"]
                            predicted_sql = node["PREDICTED_SQL"]
                            response = compare_sqls(
                                db_path=str(db_path),
                                predicted_sql=predicted_sql,
                                ground_truth_sql=ground_truth_sql,
                            )
                            node["exec_res"] = response["exec_res"]
                            node["exec_err"] = response["exec_err"]
                            evaluation_node["revision"] = node
                            evaluation_node["revision"]["exec_res"] = node["exec_res"]
                            evaluation_node["revision"]["exec_err"] = node["exec_err"]
                            evaluation_node["revision"]["question_id"] = question_id
                            evaluation_node["revision"]["db_id"] = db_id
                            evaluation_node["revision"]["question"] = node.get(
                                "question", "")
                            evaluation_node["revision"]["GOLD_SQL"] = ground_truth_sql
                            evaluation_node["revision"]["PREDICTED_SQL"] = predicted_sql
                    evaluation_node["status"] = "success"
                    result.append(evaluation_node)
                # write the updated result to the original file
                with open(os.path.join(output_directory, file), "w", encoding="utf-8") as f:
                    json.dump(result, f, indent=4)

    def statistics(self):
        print("start statistics")
        statistics_directory = self.input_result_directory
        if self.multiple_candidate:
            statistics_directory = self.input_result_directory+"_"+self.pass_at_k
        for file in os.listdir(statistics_directory):
            if "_" not in file or "predict_dev" in file:
                continue
            if file.endswith(".json") and "_" in file:
                print(file)
                _index = file.find("_")
                question_id = int(file[:_index])
                db_id = file[_index + 1:-5]
                with open(os.path.join(statistics_directory, file), "r", encoding="utf-8") as f:
                    result = json.load(f)
                    for node in result:
                        if "node_type" in node and node["node_type"] == "evaluation":
                            for evaluation_for, result in node.items():
                                if evaluation_for in ['node_type', 'status'] or node[evaluation_for] == {}:
                                    continue
                                self.statistics_manager.update_stats(
                                    db_id, question_id, evaluation_for, result)
                            self.statistics_manager.dump_statistics_to_file()


def main():
    input_result_directory = "./results/mac_on_bird_dev_deepseek/bird_dev_deepseek_v3"
    dataset_directory = ""
    output_result_directory = ""
    real_schema_directory = "./results/chess_on_dev/"
    multiple_candidate = False
    if multiple_candidate:
        pass_at_k = ["pass_at_1", "pass_at_5",
                     "pass_at_10", "pass_at_15", "pass_at_20"]
        for i in range(len(pass_at_k)):
            postprocessing_agent = PostprocessingAgent(
                input_result_directory, dataset_directory, output_result_directory, real_schema_directory, multiple_candidate, pass_at_k[i])
            postprocessing_agent.preprocess()
            postprocessing_agent.evaluate()
            postprocessing_agent.statistics()
    else:
        postprocessing_agent = PostprocessingAgent(
            input_result_directory, dataset_directory, output_result_directory, real_schema_directory, multiple_candidate)
        # postprocessing_agent.preprocess()
        # postprocessing_agent.evaluate()
        postprocessing_agent.statistics()


if __name__ == "__main__":
    main()
