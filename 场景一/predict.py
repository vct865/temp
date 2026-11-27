
from pathlib import Path
import json
import joblib
import pandas as pd

# 项目路径
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
MODEL_DIR = BASE_DIR / "model"
RESULT_DIR = BASE_DIR / "results"

# 读取预测数据
data = pd.read_csv(DATA_DIR / "Score.csv")

# 加载训练阶段保存的模型和标准化器
scaler = joblib.load(MODEL_DIR / "scaler.pkl")
model = joblib.load(MODEL_DIR / "best_model.pkl")

with open(MODEL_DIR / "label_mapping.json", "r", encoding="utf-8") as f:
    label_mapping = json.load(f)

# 检查预测数据
required_columns = ["sno", "Chinese", "Math"]
if not all(col in data.columns for col in required_columns):
    raise ValueError("Score.csv 缺少必要字段：sno、Chinese、Math")

if data[required_columns].isnull().any().any():
    raise ValueError("预测数据存在缺失值，请先检查数据")

# 只使用语文和数学成绩进行预测
X = data[["Chinese", "Math"]]

# 使用训练阶段的标准化器进行转换
X_scaled = scaler.transform(X)

# 使用最优模型预测聚类编号
cluster_labels = model.predict(X_scaled)

# 添加聚类编号和群体标签
result = data.copy()
result["cluster"] = cluster_labels
result["group"] = [
    label_mapping[str(int(label))]
    for label in cluster_labels
]

# 保存预测结果
RESULT_DIR.mkdir(exist_ok=True)
output_path = RESULT_DIR / "predict_result.csv"
result.to_csv(output_path, index=False, encoding="utf-8-sig")

# 输出预测统计
print("========== 学生群体预测完成 ==========")
print(f"预测学生数量：{len(result)}")
print("\n各群体人数：")
print(result["group"].value_counts())
print(f"\n预测结果已保存至：{output_path}")
print("\n预测结果预览：")
print(result.head(10))
