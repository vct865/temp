
from pathlib import Path
import json
import joblib
import pandas as pd

from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.mixture import GaussianMixture
from sklearn.metrics import (
    silhouette_score,
    calinski_harabasz_score,
    davies_bouldin_score
)

# ==================== 路径配置 ====================

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
MODEL_DIR = BASE_DIR / "model"
RESULT_DIR = BASE_DIR / "results"

MODEL_DIR.mkdir(exist_ok=True)
RESULT_DIR.mkdir(exist_ok=True)

# ==================== 读取数据 ====================

print("========== 读取训练数据 ==========")

data = pd.read_csv(DATA_DIR / "Score_train.csv")
X = data[["Chinese", "Math"]]

print("训练集规模：", X.shape)

# ==================== 数据标准化 ====================

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

print("\n数据标准化完成！")

# ==================== 模型训练与评价 ====================

def evaluate_model(name, model):
    labels = model.fit_predict(X_scaled)

    result = {
        "模型": name,
        "Silhouette": silhouette_score(X_scaled, labels),
        "Calinski-Harabasz": calinski_harabasz_score(
            X_scaled, labels
        ),
        "Davies-Bouldin": davies_bouldin_score(
            X_scaled, labels
        )
    }

    return result, labels


print("\n========== 训练 KMeans ==========")

kmeans = KMeans(
    n_clusters=4,
    random_state=42,
    n_init=10
)

kmeans_result, kmeans_labels = evaluate_model(
    "KMeans", kmeans
)

print("KMeans 训练完成！")

print("\n========== 训练 GMM ==========")

gmm = GaussianMixture(
    n_components=4,
    random_state=42,
    n_init=10
)

gmm.fit(X_scaled)
gmm_labels = gmm.predict(X_scaled)

gmm_result = {
    "模型": "GMM",
    "Silhouette": silhouette_score(X_scaled, gmm_labels),
    "Calinski-Harabasz": calinski_harabasz_score(
        X_scaled, gmm_labels
    ),
    "Davies-Bouldin": davies_bouldin_score(
        X_scaled, gmm_labels
    )
}

print("GMM 训练完成！")

# ==================== 模型比较 ====================

results = pd.DataFrame([kmeans_result, gmm_result])

print("\n========== 模型评价结果 ==========")
print(results.to_string(index=False))

# 三项指标排名综合比较
rank_sum = (
    results["Silhouette"].rank(ascending=False)
    + results["Calinski-Harabasz"].rank(ascending=False)
    + results["Davies-Bouldin"].rank(ascending=True)
)

best_index = rank_sum.idxmin()
best_name = results.loc[best_index, "模型"]

if best_name == "KMeans":
    best_model = kmeans
    best_labels = kmeans_labels
else:
    best_model = gmm
    best_labels = gmm_labels

print("\n综合评价最优模型：", best_name)

# ==================== 群体标签映射 ====================

if best_name == "KMeans":
    centers = best_model.cluster_centers_
else:
    centers = best_model.means_

# 将聚类中心还原为原始成绩
centers = scaler.inverse_transform(centers)

# 按两科平均成绩从低到高排列
center_scores = centers.mean(axis=1)
sorted_clusters = center_scores.argsort()

group_names = [
    "待提升型",
    "中等发展型",
    "良好发展型",
    "优秀发展型"
]

label_mapping = {
    int(cluster): group_names[index]
    for index, cluster in enumerate(sorted_clusters)
}

print("\n========== 群体标签 ==========")
for cluster, group in label_mapping.items():
    print(f"聚类编号 {cluster}：{group}")

# ==================== 保存必要文件 ====================

joblib.dump(scaler, MODEL_DIR / "scaler.pkl")
joblib.dump(best_model, MODEL_DIR / "best_model.pkl")

with open(
    MODEL_DIR / "label_mapping.json",
    "w",
    encoding="utf-8"
) as f:
    json.dump(label_mapping, f, ensure_ascii=False, indent=4)

results.to_csv(
    RESULT_DIR / "model_evaluation.csv",
    index=False,
    encoding="utf-8-sig"
)

train_result = data.copy()
train_result["cluster"] = best_labels
train_result["group"] = [
    label_mapping[int(label)] for label in best_labels
]

train_result.to_csv(
    RESULT_DIR / "train_cluster_result.csv",
    index=False,
    encoding="utf-8-sig"
)

print("\n========== 模型训练完成 ==========")
print("模型、标准化器、标签映射和训练结果已保存！")
