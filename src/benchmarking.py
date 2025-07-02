
import json
import os
from pathlib import Path
from typing import Any
from utils import calculate_table_metrics_chess, calculate_column_metrics_chess, calculate_table_metrics, calculate_column_metrics


class BenchmarkingAgent():
    def __init__(self, result_directory: str, dataset_directory: str, output_file: str):
        self.result_directory = result_directory
        self.dataset_directory = dataset_directory
        self.output_file = output_file

    def table_selection(self):
        print("table selection")
        total_precision, total_recall, total_f1_score = 0, 0, 0
        count = 0
        for file in os.listdir(self.result_directory):
            if file.endswith(".json") and "_" in file:
                _index = file.find("_")
                try:
                    question_id = int(file[:_index])
                    db_id = file[_index + 1:-5]
                except:
                    print(file)
                    continue
                with open(os.path.join(self.result_directory, file), 'r') as f:
                    exec_history = json.load(f)
                    for step in exec_history:
                        if step["node_type"] == "schema_extraction":
                            precision, recall, f1_score = calculate_table_metrics(
                                step["extracted_schema"], step["real_schema"])
                            total_precision += precision
                            total_recall += recall
                            total_f1_score += f1_score
                            count += 1
        precision = total_precision / count
        recall = total_recall / count
        f1_score = total_f1_score / count
        return {"precision": precision, "recall": recall, "f1_score": f1_score}

    def column_selection(self):
        print("column selection")
        total_precision, total_recall, total_f1_score = 0, 0, 0
        count = 0
        for file in os.listdir(self.result_directory):
            if file.endswith(".json") and "_" in file:
                _index = file.find("_")
                try:
                    question_id = int(file[:_index])
                    db_id = file[_index + 1:-5]
                except:
                    print(file)
                    continue
                with open(os.path.join(self.result_directory, file), 'r') as f:
                    exec_history = json.load(f)
                    for step in exec_history:
                        if step["node_type"] == "schema_extraction":
                            precision, recall, f1_score = calculate_column_metrics(
                                step["extracted_schema"], step["real_schema"])
                            total_precision += precision
                            total_recall += recall
                            total_f1_score += f1_score
                            count += 1
        precision = total_precision / count
        recall = total_recall / count
        f1_score = total_f1_score / count
        return {"precision": precision, "recall": recall, "f1_score": f1_score}

    def candidate_generation_results_analysis(self):
        print("candidate generation results analysis")
        results = {"all": {"correct": 0, "incorrect": 0, "error": 0, "total": 0}}
        statistics_file_path = Path(self.result_directory) / "-statistics.json"
        with statistics_file_path.open('r') as f:
            statistics = json.load(f)
            candidate_generation = statistics["counts"]["candidate_generation"]
            results["all"]["correct"] = candidate_generation["correct"]
            results["all"]["incorrect"] = candidate_generation["incorrect"]
            results["all"]["error"] = candidate_generation["error"]
            results["all"]["total"] = candidate_generation["total"]

            ids_candidates = statistics["ids"]["candidate_generation"]
            results["simple"] = {"correct": 0,
                                 "incorrect": 0, "error": 0, "total": 0}
            results["moderate"] = {"correct": 0,
                                   "incorrect": 0, "error": 0, "total": 0}
            results["challenging"] = {"correct": 0,
                                      "incorrect": 0, "error": 0, "total": 0}
            with open(self.dataset_directory, 'r') as f:
                dataset = json.load(f)
                for result_class, result_list in ids_candidates.items():
                    for result in result_list:
                        db_id = result[0]
                        question_id = result[1]
                        for data in dataset:
                            if data["db_id"] == db_id and data["question_id"] == question_id:
                                difficulty = data["difficulty"]
                                results[difficulty]["total"] += 1
                                if result_class == "correct":
                                    results[difficulty]["correct"] += 1
                                elif result_class == "incorrect":
                                    results[difficulty]["incorrect"] += 1
                                else:
                                    results[difficulty]["error"] += 1
        return results

    def candidate_generation_incorrect_analysis(self):
        print("candidate generation incorrect analysis")
        statistics_file_path = Path(self.result_directory) / "-statistics.json"
        with statistics_file_path.open('r') as f:
            statistics = json.load(f)
            candidate_generation = statistics["counts"]["candidate_generation"]
            candidate_generation_incorrect = candidate_generation["incorrect"]
            candidate_generation_total = candidate_generation["total"]
            incorrect_rate = candidate_generation_incorrect / candidate_generation_total
            incorrect_ids = statistics["ids"]["candidate_generation"]["incorrect"]
            incorrect_analysis = {}
            with open(self.dataset_directory, 'r') as f:
                dataset = json.load(f)
                for incorrect_id in incorrect_ids:
                    db_id = incorrect_id[0]
                    question_id = incorrect_id[1]
                    for data in dataset:
                        if data["db_id"] == db_id and data["question_id"] == question_id:
                            difficulty = data["difficulty"]
                            if difficulty not in incorrect_analysis:
                                incorrect_analysis[difficulty] = 0
                            incorrect_analysis[difficulty] += 1
        return {"incorrect_rate": incorrect_rate, "incorrect_analysis": incorrect_analysis}

    def candidate_generation_error_analysis(self):
        print("candidate generation error analysis")
        statistics_file_path = Path(self.result_directory) / "-statistics.json"
        with statistics_file_path.open('r') as f:
            statistics = json.load(f)
            candidate_generation = statistics["counts"]["candidate_generation"]
            candidate_generation_error = candidate_generation["error"]
            candidate_generation_total = candidate_generation["total"]
            error_rate = candidate_generation_error / candidate_generation_total
            error_ids = statistics["ids"]["candidate_generation"]["error"]
            error_types = {"timeout", "no such table",
                           "no such column", "syntax error", "no such function", }
            error_analysis = {}
            for error_id in error_ids:
                db_id = error_id[0]
                question_id = error_id[1]
                error_reason = error_id[2]
                known_error_type = False
                for error_type in error_types:
                    if error_type in error_reason:
                        if error_type not in error_analysis:
                            error_analysis[error_type] = 0
                        error_analysis[error_type] += 1
                        known_error_type = True
                if not known_error_type:
                    if "others" not in error_analysis:
                        error_analysis["others"] = 0
                    error_analysis["others"] += 1
        return {"error_rate": error_rate, "error_analysis": error_analysis}

    def revision_results_analysis(self):
        print("revision results analysis")
        results = {"all": {"correct": 0, "incorrect": 0, "error": 0, "total": 0}}
        statistics_file_path = Path(self.result_directory) / "-statistics.json"
        with statistics_file_path.open('r') as f:
            statistics = json.load(f)
            revision = statistics["counts"]["revision"]
            results["all"]["correct"] = revision["correct"]
            results["all"]["incorrect"] = revision["incorrect"]
            results["all"]["error"] = revision["error"]
            results["all"]["total"] = revision["total"]

            ids_revision = statistics["ids"]["revision"]
            results["simple"] = {"correct": 0,
                                 "incorrect": 0, "error": 0, "total": 0}
            results["moderate"] = {"correct": 0,
                                   "incorrect": 0, "error": 0, "total": 0}
            results["challenging"] = {"correct": 0,
                                      "incorrect": 0, "error": 0, "total": 0}
            with open(self.dataset_directory, 'r') as f:
                dataset = json.load(f)
                for result_class, result_list in ids_revision.items():
                    for result in result_list:
                        db_id = result[0]
                        question_id = result[1]
                        for data in dataset:
                            if data["db_id"] == db_id and data["question_id"] == question_id:
                                difficulty = data["difficulty"]
                                results[difficulty]["total"] += 1
                                if result_class == "correct":
                                    results[difficulty]["correct"] += 1
                                elif result_class == "incorrect":
                                    results[difficulty]["incorrect"] += 1
                                else:
                                    results[difficulty]["error"] += 1
        return results

    def revision_incorrect_analysis(self):
        print("revision incorrect analysis")
        statistics_file_path = Path(self.result_directory) / "-statistics.json"
        with statistics_file_path.open('r') as f:
            statistics = json.load(f)
            revision = statistics["counts"]["revision"]
            revision_incorrect = revision["incorrect"]
            revision_total = revision["total"]
            incorrect_rate = revision_incorrect / revision_total
            incorrect_ids = statistics["ids"]["revision"]["incorrect"]
            incorrect_analysis = {}
            with open(self.dataset_directory, 'r') as f:
                dataset = json.load(f)
                for incorrect_id in incorrect_ids:
                    db_id = incorrect_id[0]
                    question_id = incorrect_id[1]
                    for data in dataset:
                        if data["db_id"] == db_id and data["question_id"] == question_id:
                            difficulty = data["difficulty"]
                            if difficulty not in incorrect_analysis:
                                incorrect_analysis[difficulty] = 0
                            incorrect_analysis[difficulty] += 1
        return {"incorrect_rate": incorrect_rate, "incorrect_analysis": incorrect_analysis}

    def revision_error_analysis(self):
        print("revision error analysis")
        statistics_file_path = Path(self.result_directory) / "-statistics.json"
        with statistics_file_path.open('r') as f:
            statistics = json.load(f)
            revision = statistics["counts"]["revision"]
            revision_error = revision["error"]
            revision_total = revision["total"]
            error_rate = revision_error / revision_total
            error_ids = statistics["ids"]["revision"]["error"]
            error_types = {"timeout", "no such table",
                           "no such column", "syntax error", "no such function", }
            error_analysis = {}
            for error_id in error_ids:
                db_id = error_id[0]
                question_id = error_id[1]
                error_reason = error_id[2]
                known_error_type = False
                for error_type in error_types:
                    if error_type in error_reason:
                        if error_type not in error_analysis:
                            error_analysis[error_type] = 0
                        error_analysis[error_type] += 1
                        known_error_type = True
                if not known_error_type:
                    if "others" not in error_analysis:
                        error_analysis["others"] = 0
                    error_analysis["others"] += 1
        return {"error_rate": error_rate, "error_analysis": error_analysis}

    def revision_effectiveness_analysis(self):
        # return:
        # 1. correctness rate improvement percentage (from candidate generation to revision)
        # 2. the ability to correct wrong answers (incorrect, error) to correct answers
        # 3. the percentage of make correct answers to incorrect and error answers
        print("revision effectiveness analysis")
        statistics_file_path = Path(self.result_directory) / "-statistics.json"
        with statistics_file_path.open('r') as f:
            statistics = json.load(f)
            revision = statistics["counts"]["revision"]
            revision_correct = revision["correct"]
            revision_incorrect = revision["incorrect"]
            revision_error = revision["error"]
            candidate_generation = statistics["counts"]["candidate_generation"]
            candidate_generation_correct = candidate_generation["correct"]
            candidate_generation_incorrect = candidate_generation["incorrect"]
            candidate_generation_error = candidate_generation["error"]
            revision_correctness_rate = revision_correct / revision["total"]
            candidate_generation_correctness_rate = candidate_generation_correct / \
                candidate_generation["total"]
            correctness_rate_improvement = (
                revision_correctness_rate - candidate_generation_correctness_rate) / candidate_generation_correctness_rate

            revisions = statistics["ids"]["revision"]
            candidate_generations = statistics["ids"]["candidate_generation"]
            revisions_correct_ids = [ele[1] for ele in revisions["correct"]]
            revisions_incorrect_ids = [ele[1]
                                       for ele in revisions["incorrect"]]
            revisions_error_ids = [ele[1] for ele in revisions["error"]]
            candidate_generations_correct_ids = [
                ele[1] for ele in candidate_generations["correct"]]
            candidate_generations_incorrect_ids = [
                ele[1] for ele in candidate_generations["incorrect"]]
            candidate_generations_error_ids = [ele[1]
                                               for ele in candidate_generations["error"]]
            incorrect_to_correct = 0
            error_to_correct = 0
            for revision_id in revisions_correct_ids:
                if revision_id in candidate_generations_incorrect_ids:
                    incorrect_to_correct += 1
            for revision_id in revisions_correct_ids:
                if revision_id in candidate_generations_error_ids:
                    error_to_correct += 1
            incorrect_to_correct_rate = incorrect_to_correct / candidate_generation_incorrect
            error_to_correct_rate = error_to_correct / candidate_generation_error

            correct_to_incorrect = 0
            correct_to_error = 0
            for revision_id in revisions_incorrect_ids:
                if revision_id in candidate_generations_correct_ids:
                    correct_to_incorrect += 1
            for revision_id in revisions_error_ids:
                if revision_id in candidate_generations_correct_ids:
                    correct_to_error += 1
            correct_to_incorrect_rate = correct_to_incorrect / candidate_generation_correct
            correct_to_error_rate = correct_to_error / candidate_generation_correct
        return {"correctness_rate_improvement": correctness_rate_improvement, "incorrect_to_correct_rate": incorrect_to_correct_rate, "error_to_correct_rate": error_to_correct_rate, "correct_to_incorrect_rate": correct_to_incorrect_rate, "correct_to_error_rate": correct_to_error_rate}

    def token_and_time_cost_analysis(self):
        print("token and time cost analysis")
        total_prompt_tokens, total_completion_tokens, total_total_tokens, total_call_llm_times, total_llm_time, total_duration = {"schema_extraction": [], "candidate_generation": [], "revision": []}, {"schema_extraction": [], "candidate_generation": [
        ], "revision": []}, {"schema_extraction": [], "candidate_generation": [], "revision": []}, {"schema_extraction": [], "candidate_generation": [], "revision": []}, {"schema_extraction": [], "candidate_generation": [], "revision": []}, {"schema_extraction": [], "candidate_generation": [], "revision": []}
        schema_extraction, candiate_generation, revision = {}, {}, {}
        for file in os.listdir(self.result_directory):
            if file.endswith(".json") and "_" in file:
                _index = file.find("_")
                try:
                    question_id = int(file[:_index])
                    db_id = file[_index + 1:-5]
                except:
                    print(file)
                    continue
                with open(os.path.join(self.result_directory, file), 'r') as f:
                    exec_history = json.load(f)
                    for step in exec_history:
                        if "node_type" in step and step["node_type"] == "schema_extraction":
                            prompt_tokens = step.get("prompt_tokens", 0)
                            completion_tokens = step.get(
                                "completion_tokens", 0)
                            total_tokens = step.get("total_tokens", 0)
                            call_llm_times = step.get("call_llm_times", 0)
                            llm_time = step.get("llm_time", 0)
                            duration = step.get("duration", 0)
                            if prompt_tokens != 0:
                                total_prompt_tokens["schema_extraction"].append(
                                    prompt_tokens)
                            if completion_tokens != 0:
                                total_completion_tokens["schema_extraction"].append(
                                    completion_tokens)
                            if total_tokens != 0:
                                total_total_tokens["schema_extraction"].append(
                                    total_tokens)
                            if call_llm_times != 0:
                                total_call_llm_times["schema_extraction"].append(
                                    call_llm_times)
                            if llm_time != 0:
                                total_llm_time["schema_extraction"].append(
                                    llm_time)
                            if duration != 0:
                                total_duration["schema_extraction"].append(
                                    duration)
                        elif "node_type" in step and step["node_type"] == "candidate_generation":
                            prompt_tokens = step.get("prompt_tokens", 0)
                            completion_tokens = step.get(
                                "completion_tokens", 0)
                            total_tokens = step.get("total_tokens", 0)
                            call_llm_times = step.get("call_llm_times", 0)
                            llm_time = step.get("llm_time", 0)
                            duration = step.get("duration", 0)
                            if prompt_tokens != 0:
                                total_prompt_tokens["candidate_generation"].append(
                                    prompt_tokens)
                            if completion_tokens != 0:
                                total_completion_tokens["candidate_generation"].append(
                                    completion_tokens)
                            if total_tokens != 0:
                                total_total_tokens["candidate_generation"].append(
                                    total_tokens)
                            if call_llm_times != 0:
                                total_call_llm_times["candidate_generation"].append(
                                    call_llm_times)
                            if llm_time != 0:
                                total_llm_time["candidate_generation"].append(
                                    llm_time)
                            if duration != 0:
                                total_duration["candidate_generation"].append(
                                    duration)
                        elif "node_type" in step and step["node_type"] == "revision":
                            prompt_tokens = step.get("prompt_tokens", 0)
                            completion_tokens = step.get(
                                "completion_tokens", 0)
                            total_tokens = step.get("total_tokens", 0)
                            call_llm_times = step.get("call_llm_times", 0)
                            llm_time = step.get("llm_time", 0)
                            duration = step.get("duration", 0)
                            if prompt_tokens != 0:
                                total_prompt_tokens["revision"].append(
                                    prompt_tokens)
                            if completion_tokens != 0:
                                total_completion_tokens["revision"].append(
                                    completion_tokens)
                            if total_tokens != 0:
                                total_total_tokens["revision"].append(
                                    total_tokens)
                            if call_llm_times != 0:
                                total_call_llm_times["revision"].append(
                                    call_llm_times)
                            if llm_time != 0:
                                total_llm_time["revision"].append(llm_time)
                            if duration != 0:
                                total_duration["revision"].append(duration)

        # calculate the average for schema_extraction
        if len(total_prompt_tokens["schema_extraction"]) == 0:
            schema_extraction["prompt_tokens"] = 0
        else:
            schema_extraction["prompt_tokens"] = sum(
                total_prompt_tokens["schema_extraction"])/len(total_prompt_tokens["schema_extraction"])
        if len(total_completion_tokens["schema_extraction"]) == 0:
            schema_extraction["completion_tokens"] = 0
        else:
            schema_extraction["completion_tokens"] = sum(
                total_completion_tokens["schema_extraction"])/len(total_completion_tokens["schema_extraction"])
        if len(total_total_tokens["schema_extraction"]) == 0:
            schema_extraction["total_tokens"] = 0
        else:
            schema_extraction["total_tokens"] = sum(
                total_total_tokens["schema_extraction"])/len(total_total_tokens["schema_extraction"])
        if len(total_call_llm_times["schema_extraction"]) == 0:
            schema_extraction["call_llm_times"] = 0
        else:
            schema_extraction["call_llm_times"] = sum(
                total_call_llm_times["schema_extraction"])/len(total_call_llm_times["schema_extraction"])
        if len(total_llm_time["schema_extraction"]) == 0:
            schema_extraction["llm_time"] = 0
        else:
            schema_extraction["llm_time"] = sum(
                total_llm_time["schema_extraction"])/len(total_llm_time["schema_extraction"])
        if len(total_duration["schema_extraction"]) == 0:
            schema_extraction["duration"] = 0
        else:
            schema_extraction["duration"] = sum(
                total_duration["schema_extraction"])/len(total_duration["schema_extraction"])

        # calculate the average for candidate_generation
        if len(total_prompt_tokens["candidate_generation"]) == 0:
            candiate_generation["prompt_tokens"] = 0
        else:
            candiate_generation["prompt_tokens"] = sum(
                total_prompt_tokens["candidate_generation"])/len(total_prompt_tokens["candidate_generation"])
        if len(total_completion_tokens["candidate_generation"]) == 0:
            candiate_generation["completion_tokens"] = 0
        else:
            candiate_generation["completion_tokens"] = sum(
                total_completion_tokens["candidate_generation"])/len(total_completion_tokens["candidate_generation"])
        if len(total_total_tokens["candidate_generation"]) == 0:
            candiate_generation["total_tokens"] = 0
        else:
            candiate_generation["total_tokens"] = sum(
                total_total_tokens["candidate_generation"])/len(total_total_tokens["candidate_generation"])
        if len(total_call_llm_times["candidate_generation"]) == 0:
            candiate_generation["call_llm_times"] = 0
        else:
            candiate_generation["call_llm_times"] = sum(
                total_call_llm_times["candidate_generation"])/len(total_call_llm_times["candidate_generation"])
        if len(total_llm_time["candidate_generation"]) == 0:
            candiate_generation["llm_time"] = 0
        else:
            candiate_generation["llm_time"] = sum(
                total_llm_time["candidate_generation"])/len(total_llm_time["candidate_generation"])
        if len(total_duration["candidate_generation"]) == 0:
            candiate_generation["duration"] = 0
        else:
            candiate_generation["duration"] = sum(
                total_duration["candidate_generation"])/len(total_duration["candidate_generation"])

        # calculate the average for revision
        if len(total_prompt_tokens["revision"]) == 0:
            revision["prompt_tokens"] = 0
        else:
            revision["prompt_tokens"] = sum(
                total_prompt_tokens["revision"])/len(total_prompt_tokens["revision"])
        if len(total_completion_tokens["revision"]) == 0:
            revision["completion_tokens"] = 0
        else:
            revision["completion_tokens"] = sum(
                total_completion_tokens["revision"])/len(total_completion_tokens["revision"])
        if len(total_total_tokens["revision"]) == 0:
            revision["total_tokens"] = 0
        else:
            revision["total_tokens"] = sum(
                total_total_tokens["revision"])/len(total_total_tokens["revision"])
        if len(total_call_llm_times["revision"]) == 0:
            revision["call_llm_times"] = 0
        else:
            revision["call_llm_times"] = sum(
                total_call_llm_times["revision"])/len(total_call_llm_times["revision"])
        if len(total_llm_time["revision"]) == 0:
            revision["llm_time"] = 0
        else:
            revision["llm_time"] = sum(
                total_llm_time["revision"])/len(total_llm_time["revision"])
        if len(total_duration["revision"]) == 0:
            revision["duration"] = 0
        else:
            revision["duration"] = sum(
                total_duration["revision"])/len(total_duration["revision"])

        total = {
            "prompt_tokens": schema_extraction["prompt_tokens"] + candiate_generation["prompt_tokens"] + revision["prompt_tokens"],
            "completion_tokens": schema_extraction["completion_tokens"] + candiate_generation["completion_tokens"] + revision["completion_tokens"],
            "total_tokens": schema_extraction["total_tokens"] + candiate_generation["total_tokens"] + revision["total_tokens"],
            "call_llm_times": schema_extraction["call_llm_times"] + candiate_generation["call_llm_times"] + revision["call_llm_times"],
            "llm_time": schema_extraction["llm_time"] + candiate_generation["llm_time"] + revision["llm_time"],
            "duration": schema_extraction["duration"] + candiate_generation["duration"] + revision["duration"]
        }
        return {"schema_extraction": schema_extraction, "candidate_generation": candiate_generation, "revision": revision, "total": total}
        total_prompt_tokens, total_completion_tokens, total_total_tokens, total_call_llm_times, total_llm_time, total_duration = {"schema_extraction": [], "candidate_generation": [], "revision": []}, {"schema_extraction": [], "candidate_generation": [
        ], "revision": []}, {"schema_extraction": [], "candidate_generation": [], "revision": []}, {"schema_extraction": [], "candidate_generation": [], "revision": []}, {"schema_extraction": [], "candidate_generation": [], "revision": []}, {"schema_extraction": [], "candidate_generation": [], "revision": []}
        schema_extraction, candiate_generation, revision = {}, {}, {}
        for file in os.listdir(self.result_directory):
            if file.endswith(".json") and "_" in file:
                _index = file.find("_")
                try:
                    question_id = int(file[:_index])
                    db_id = file[_index + 1:-5]
                except:
                    print(file)
                    continue
                with open(os.path.join(self.result_directory, file), 'r') as f:
                    exec_history = json.load(f)
                    prompt_tokens_sum, completion_tokens_sum, total_tokens_sum, call_llm_times_sum, llm_time_sum, duration_sum = 0, 0, 0, 0, 0, 0
                    for step in exec_history:
                        if "tool_name" in step and step["tool_name"] == "schema_extraction":
                            prompt_tokens = step.get("prompt_tokens", 0)
                            completion_tokens = step.get(
                                "completion_tokens", 0)
                            total_tokens = step.get("total_tokens", 0)
                            call_llm_times = step.get("call_llm_times", 0)
                            llm_time = step.get("llm_time", 0)
                            duration = step.get("duration", 0)
                            if prompt_tokens != 0:
                                total_prompt_tokens["schema_extraction"].append(
                                    prompt_tokens)
                            if completion_tokens != 0:
                                total_completion_tokens["schema_extraction"].append(
                                    completion_tokens)
                            if total_tokens != 0:
                                total_total_tokens["schema_extraction"].append(
                                    total_tokens)
                            if call_llm_times != 0:
                                total_call_llm_times["schema_extraction"].append(
                                    call_llm_times)
                            if llm_time != 0:
                                total_llm_time["schema_extraction"].append(
                                    llm_time)
                            if duration != 0:
                                total_duration["schema_extraction"].append(
                                    duration)
                        elif "tool_name" in step and (step["tool_name"] in ["generate_candidate", "extract_keywords"]):
                            prompt_tokens = step.get("prompt_tokens", 0)
                            completion_tokens = step.get(
                                "completion_tokens", 0)
                            total_tokens = step.get("total_tokens", 0)
                            call_llm_times = step.get("call_llm_times", 0)
                            if step["tool_name"] == "generate_candidate":
                                call_llm_times *= 2
                            llm_time = step.get("llm_time", 0)
                            duration = step.get("duration", 0)
                            prompt_tokens_sum += prompt_tokens
                            completion_tokens_sum += completion_tokens
                            total_tokens_sum += total_tokens
                            call_llm_times_sum += call_llm_times
                            llm_time_sum += llm_time
                            duration_sum += duration
                            if prompt_tokens_sum != 0 and step["tool_name"] == "generate_candidate":
                                total_prompt_tokens["candidate_generation"].append(
                                    prompt_tokens_sum)
                            if completion_tokens_sum != 0 and step["tool_name"] == "generate_candidate":
                                total_completion_tokens["candidate_generation"].append(
                                    completion_tokens_sum)
                            if total_tokens_sum != 0 and step["tool_name"] == "generate_candidate":
                                total_total_tokens["candidate_generation"].append(
                                    total_tokens_sum)
                            if call_llm_times_sum != 0 and step["tool_name"] == "generate_candidate":
                                total_call_llm_times["candidate_generation"].append(
                                    call_llm_times_sum)
                            if llm_time_sum != 0 and step["tool_name"] == "generate_candidate":
                                total_llm_time["candidate_generation"].append(
                                    llm_time_sum)
                            if duration_sum != 0 and step["tool_name"] == "generate_candidate":
                                total_duration["candidate_generation"].append(
                                    duration_sum)
                            prompt_tokens_sum, completion_tokens_sum, total_tokens_sum, call_llm_times_sum, llm_time_sum, duration_sum = 0, 0, 0, 0, 0, 0
                        elif "tool_name" in step and step["tool_name"] in ["revise", "generate_unit_test", "evaluate"]:
                            prompt_tokens = step.get("prompt_tokens", 0)
                            completion_tokens = step.get(
                                "completion_tokens", 0)
                            total_tokens = step.get("total_tokens", 0)
                            call_llm_times = step.get("call_llm_times", 0)
                            llm_time = step.get("llm_time", 0)
                            duration = step.get("duration", 0)
                            prompt_tokens_sum += prompt_tokens
                            completion_tokens_sum += completion_tokens
                            total_tokens_sum += total_tokens
                            call_llm_times_sum += call_llm_times
                            llm_time_sum += llm_time
                            duration_sum += duration
                            if prompt_tokens_sum != 0 and step["tool_name"] == "evaluate":
                                total_prompt_tokens["revision"].append(
                                    prompt_tokens_sum)
                            if completion_tokens_sum != 0 and step["tool_name"] == "evaluate":
                                total_completion_tokens["revision"].append(
                                    completion_tokens_sum)
                            if total_tokens_sum != 0 and step["tool_name"] == "evaluate":
                                total_total_tokens["revision"].append(
                                    total_tokens_sum)
                            if call_llm_times_sum != 0 and step["tool_name"] == "evaluate":
                                total_call_llm_times["revision"].append(
                                    call_llm_times_sum)
                            if llm_time_sum != 0 and step["tool_name"] == "evaluate":
                                total_llm_time["revision"].append(
                                    llm_time_sum)
                            if duration_sum != 0 and step["tool_name"] == "evaluate":
                                total_duration["revision"].append(
                                    duration_sum)

        # calculate the average for schema_extraction
        if len(total_prompt_tokens["schema_extraction"]) == 0:
            schema_extraction["prompt_tokens"] = 0
        else:
            schema_extraction["prompt_tokens"] = sum(
                total_prompt_tokens["schema_extraction"])/len(total_prompt_tokens["schema_extraction"])
        if len(total_completion_tokens["schema_extraction"]) == 0:
            schema_extraction["completion_tokens"] = 0
        else:
            schema_extraction["completion_tokens"] = sum(
                total_completion_tokens["schema_extraction"])/len(total_completion_tokens["schema_extraction"])
        if len(total_total_tokens["schema_extraction"]) == 0:
            schema_extraction["total_tokens"] = 0
        else:
            schema_extraction["total_tokens"] = sum(
                total_total_tokens["schema_extraction"])/len(total_total_tokens["schema_extraction"])
        if len(total_call_llm_times["schema_extraction"]) == 0:
            schema_extraction["call_llm_times"] = 0
        else:
            schema_extraction["call_llm_times"] = sum(
                total_call_llm_times["schema_extraction"])/len(total_call_llm_times["schema_extraction"])
        if len(total_llm_time["schema_extraction"]) == 0:
            schema_extraction["llm_time"] = 0
        else:
            schema_extraction["llm_time"] = sum(
                total_llm_time["schema_extraction"])/len(total_llm_time["schema_extraction"])
        if len(total_duration["schema_extraction"]) == 0:
            schema_extraction["duration"] = 0
        else:
            schema_extraction["duration"] = sum(
                total_duration["schema_extraction"])/len(total_duration["schema_extraction"])

        # calculate the average for candidate_generation
        if len(total_prompt_tokens["candidate_generation"]) == 0:
            candiate_generation["prompt_tokens"] = 0
        else:
            candiate_generation["prompt_tokens"] = sum(
                total_prompt_tokens["candidate_generation"])/len(total_prompt_tokens["candidate_generation"])
        if len(total_completion_tokens["candidate_generation"]) == 0:
            candiate_generation["completion_tokens"] = 0
        else:
            candiate_generation["completion_tokens"] = sum(
                total_completion_tokens["candidate_generation"])/len(total_completion_tokens["candidate_generation"])
        if len(total_total_tokens["candidate_generation"]) == 0:
            candiate_generation["total_tokens"] = 0
        else:
            candiate_generation["total_tokens"] = sum(
                total_total_tokens["candidate_generation"])/len(total_total_tokens["candidate_generation"])
        if len(total_call_llm_times["candidate_generation"]) == 0:
            candiate_generation["call_llm_times"] = 0
        else:
            candiate_generation["call_llm_times"] = sum(
                total_call_llm_times["candidate_generation"])/len(total_call_llm_times["candidate_generation"])
        if len(total_llm_time["candidate_generation"]) == 0:
            candiate_generation["llm_time"] = 0
        else:
            candiate_generation["llm_time"] = sum(
                total_llm_time["candidate_generation"])/len(total_llm_time["candidate_generation"])
        if len(total_duration["candidate_generation"]) == 0:
            candiate_generation["duration"] = 0
        else:
            candiate_generation["duration"] = sum(
                total_duration["candidate_generation"])/len(total_duration["candidate_generation"])

        # calculate the average for revision
        if len(total_prompt_tokens["revision"]) == 0:
            revision["prompt_tokens"] = 0
        else:
            revision["prompt_tokens"] = sum(
                total_prompt_tokens["revision"])/len(total_prompt_tokens["revision"])
        if len(total_completion_tokens["revision"]) == 0:
            revision["completion_tokens"] = 0
        else:
            revision["completion_tokens"] = sum(
                total_completion_tokens["revision"])/len(total_completion_tokens["revision"])
        if len(total_total_tokens["revision"]) == 0:
            revision["total_tokens"] = 0
        else:
            revision["total_tokens"] = sum(
                total_total_tokens["revision"])/len(total_total_tokens["revision"])
        if len(total_call_llm_times["revision"]) == 0:
            revision["call_llm_times"] = 0
        else:
            revision["call_llm_times"] = sum(
                total_call_llm_times["revision"])/len(total_call_llm_times["revision"])
        if len(total_llm_time["revision"]) == 0:
            revision["llm_time"] = 0
        else:
            revision["llm_time"] = sum(
                total_llm_time["revision"])/len(total_llm_time["revision"])
        if len(total_duration["revision"]) == 0:
            revision["duration"] = 0
        else:
            revision["duration"] = sum(
                total_duration["revision"])/len(total_duration["revision"])

        total = {
            "prompt_tokens": schema_extraction["prompt_tokens"] + candiate_generation["prompt_tokens"] + revision["prompt_tokens"],
            "completion_tokens": schema_extraction["completion_tokens"] + candiate_generation["completion_tokens"] + revision["completion_tokens"],
            "total_tokens": schema_extraction["total_tokens"] + candiate_generation["total_tokens"] + revision["total_tokens"],
            "call_llm_times": schema_extraction["call_llm_times"] + candiate_generation["call_llm_times"] + revision["call_llm_times"],
            "llm_time": schema_extraction["llm_time"] + candiate_generation["llm_time"] + revision["llm_time"],
            "duration": schema_extraction["duration"] + candiate_generation["duration"] + revision["duration"]
        }
        return {"schema_extraction": schema_extraction, "candidate_generation": candiate_generation, "revision": revision, "total": total}


def main():
    schema = "original"  # "original" or "gold"
    method = "e"  # "din", "mac", "ta", "c3", "chess_v1", "chess_v2", "gsr", "rsl", "e", "opensearch"
    if schema == "original":
        result_directory = f"./results/{method}_on_bird_dev_deepseek/bird_dev_deepseek_v3"
        output_file = f"./results/{method}_on_bird_dev_deepseek/bird_dev_deepseek_v3/~analysis.json"
    else:
        result_directory = f"./results/{method}_on_bird_dev_deepseek/bird_dev_deepseek_v3_gold"
        output_file = f"./results/{method}_on_bird_dev_deepseek/bird_dev_deepseek_v3_gold/~analysis.json"
    dataset_directory = "./data/dev/dev_merge.json"

    benchmarking_agent = BenchmarkingAgent(
        result_directory, dataset_directory, output_file)
    table_selection_results = benchmarking_agent.table_selection()
    column_selection_results = benchmarking_agent.column_selection()
    candidate_generation_results_analysis_results = benchmarking_agent.candidate_generation_results_analysis()
    candidate_generation_incorrect_analysis_results = benchmarking_agent.candidate_generation_incorrect_analysis()
    candidate_generation_error_analysis_results = benchmarking_agent.candidate_generation_error_analysis()
    revision_results_analysis_results = benchmarking_agent.revision_results_analysis()
    revision_incorrect_analysis_results = benchmarking_agent.revision_incorrect_analysis()
    revision_error_analysis_results = benchmarking_agent.revision_error_analysis()
    revision_effectiveness_analysis_results = benchmarking_agent.revision_effectiveness_analysis()
    token_and_time_cost_analysis_results = benchmarking_agent.token_and_time_cost_analysis()
    with open(output_file, 'w') as f:
        json.dump({
            "table_selection_results": table_selection_results,
            "column_selection_results": column_selection_results,
            "candidate_generation_results_analysis_results": candidate_generation_results_analysis_results,
            "candidate_generation_incorrect_analysis_results": candidate_generation_incorrect_analysis_results,
            "candidate_generation_error_analysis_results": candidate_generation_error_analysis_results,
            "revision_results_analysis_results": revision_results_analysis_results,
            "revision_incorrect_analysis_results": revision_incorrect_analysis_results,
            "revision_error_analysis_results": revision_error_analysis_results,
            "revision_effectiveness_analysis_results": revision_effectiveness_analysis_results,
            "token_and_time_cost_analysis_results": token_and_time_cost_analysis_results
        }, f, indent=4)


if __name__ == '__main__':
    main()
