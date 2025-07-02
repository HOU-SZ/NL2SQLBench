def calculate_table_metrics_chess(selected_tables, correct_columns):
    # 提取正确的表集合
    correct_tables = set(correct_columns.keys())
    # 全部转为小写
    correct_tables = {table.lower() for table in correct_tables}

    # 将selected_tables转换为集合
    selected_set = set(selected_tables)
    # 全部转为小写
    selected_set = {table.lower() for table in selected_set}

    # 计算True Positives (TP)
    tp = len(selected_set & correct_tables)  # 交集

    # 计算False Positives (FP) 和 False Negatives (FN)
    fp = len(selected_set - correct_tables)  # selected但不正确
    fn = len(correct_tables - selected_set)  # 正确但未选中

    # 计算precision, recall
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0

    # 计算F1-score
    f1_score = 2 * precision * recall / \
        (precision + recall) if (precision + recall) > 0 else 0

    return precision, recall, f1_score


def calculate_table_metrics(extracted_schema, real_schema):
    # 将表名转换为小写集合
    extracted_tables = {table.lower() for table in extracted_schema.keys()}
    real_tables = {table.lower() for table in real_schema.keys()}

    # 计算True Positives (TP), False Positives (FP), False Negatives (FN)
    tp = len(extracted_tables & real_tables)  # 交集为TP
    fp = len(extracted_tables - real_tables)  # extracted中有但real中没有
    fn = len(real_tables - extracted_tables)  # real中有但extracted中没有

    # 计算Precision, Recall
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0

    # 计算F1-score
    f1_score = 2 * precision * recall / \
        (precision + recall) if (precision + recall) > 0 else 0

    return precision, recall, f1_score


def calculate_column_metrics_chess(model_selected_columns, correct_columns):
    # 将extracted_schema和real_schema的key和value全部转换为小写
    extracted_schema = {table.lower(): [col.lower(
    ) for col in columns] for table, columns in extracted_schema.items()}
    real_schema = {table.lower(): [col.lower() for col in columns]
                   for table, columns in real_schema.items()}

    # 初始化统计指标
    tp = 0  # True Positives
    fp = 0  # False Positives
    fn = 0  # False Negatives

    # 遍历model_selected_columns计算TP和FP
    for table, selected_columns in model_selected_columns.items():
        selected_set = {col.lower() for col in selected_columns}  # 转为小写集合
        correct_set = {col.lower()
                       for col in correct_columns.get(table, [])}  # 转为小写集合
        tp += len(selected_set & correct_set)  # 交集为TP
        fp += len(selected_set - correct_set)  # 差集为FP

    # 遍历correct_columns计算FN
    for table, correct_columns_list in correct_columns.items():
        correct_set = {col.lower() for col in correct_columns_list}  # 转为小写集合
        selected_set = {col.lower()
                        for col in model_selected_columns.get(table, [])}  # 转为小写集合
        fn += len(correct_set - selected_set)  # 差集为FN

    # 计算Precision, Recall
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0

    # 计算F1-score
    f1_score = 2 * precision * recall / \
        (precision + recall) if (precision + recall) > 0 else 0

    return precision, recall, f1_score


def calculate_column_metrics(extracted_schema, real_schema):
    # 将extracted_schema和real_schema的key和value全部转换为小写
    extracted_schema = {table.lower(): [col.lower(
    ) for col in columns] for table, columns in extracted_schema.items()}
    real_schema = {table.lower(): [col.lower() for col in columns]
                   for table, columns in real_schema.items()}
    # 初始化统计指标
    tp = 0  # True Positives
    fp = 0  # False Positives
    fn = 0  # False Negatives

    # 遍历extracted_schema计算TP和FP
    for table, extracted_columns in extracted_schema.items():
        table_lower = table.lower()  # 表名小写
        extracted_set = {col.lower() for col in extracted_columns}  # 转为小写集合
        correct_set = {col.lower() for col in real_schema.get(
            table_lower, [])}  # 获取正确值，转为小写集合
        tp += len(extracted_set & correct_set)  # 交集为TP
        fp += len(extracted_set - correct_set)  # 差集为FP

    # 遍历real_schema计算FN
    for table, correct_columns in real_schema.items():
        table_lower = table.lower()  # 表名小写
        correct_set = {col.lower() for col in correct_columns}  # 转为小写集合
        extracted_set = {col.lower() for col in extracted_schema.get(
            table_lower, [])}  # 获取预测值，转为小写集合
        fn += len(correct_set - extracted_set)  # 差集为FN

    # print(tp, fp, fn)

    # 计算Precision, Recall
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0

    # 计算F1-score
    f1_score = 2 * precision * recall / \
        (precision + recall) if (precision + recall) > 0 else 0

    return precision, recall, f1_score


if __name__ == "__main__":
    # # 示例数据
    # selected_tables = ["satscores", "schools"]
    # model_selected_columns = {
    #     "satscores": ["cds", "AvgScrMath"],
    #     "schools": ["CDSCode", "FundingType", "Charter"]
    # }
    # correct_columns = {
    #     "frpm": ["School Code", "cdscode", "Charter Funding Type"],
    #     "satscores": ["cds", "avgscrmath"]
    # }

    # # 调用函数
    # precision, recall, f1_score = calculate_table_metrics(
    #     selected_tables, correct_columns)

    # # 输出结果
    # print(f"Precision: {precision:.2f}")
    # print(f"Recall: {recall:.2f}")
    # print(f"F1-score: {f1_score:.2f}")

    # precision, recall, f1_score = calculate_column_metrics(
    #     model_selected_columns, correct_columns)

    # # 输出结果
    # print(f"Precision: {precision:.2f}")
    # print(f"Recall: {recall:.2f}")
    # print(f"F1-score: {f1_score:.2f}")

    extracted_schema = {
        "Examination": [
            "ID",
            "aCL IgG",
            "Examination Date",
            "aCL IgM",
            "ANA",
            "ANA Pattern"
        ],
        "Patient": [
            "ID",
            "SEX",
            "Birthday",
            "Description",
            "First Date",
            "Admission"
        ]
    }
    real_schema = {
        "examination": [
            "aCL IgG",
            "id"
        ],
        "patient": [
            "id",
            "admission",
            "birthday"
        ]
    }

    # 调用函数
    precision, recall, f1_score = calculate_table_metrics(
        extracted_schema, real_schema)

    # 输出结果
    print(f"Precision: {precision:.2f}")
    print(f"Recall: {recall:.2f}")
    print(f"F1-score: {f1_score:.2f}")

    precision, recall, f1_score = calculate_column_metrics(
        extracted_schema, real_schema)

    # 输出结果
    print(f"Precision: {precision:.2f}")
    print(f"Recall: {recall:.2f}")
    print(f"F1-score: {f1_score:.2f}")
