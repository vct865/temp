
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# =========================
# 1. 路径配置
# =========================
BASE_DIR = Path(__file__).resolve().parent

train_path = BASE_DIR / "data" / "Score_train.csv"
test_path = BASE_DIR / "data" / "Score.csv"
result_dir = BASE_DIR / "results"

result_dir.mkdir(exist_ok=True)

# 中文显示设置
plt.rcParams["font.sans-serif"] = [
    "SimHei", "Microsoft YaHei", "Arial Unicode MS"
]
plt.rcParams["axes.unicode_minus"] = False


# =========================
# 2. 读取数据
# =========================
print("========== 读取数据 ==========")

if not train_path.exists():
    raise FileNotFoundError("找不到训练集：" + str(train_path))

if not test_path.exists():
    raise FileNotFoundError("找不到预测集：" + str(test_path))

train_data = pd.read_csv(train_path, encoding="utf-8-sig")
test_data = pd.read_csv(test_path, encoding="utf-8-sig")

print("训练集读取成功！")
print("预测集读取成功！")


# =========================
# 3. 检查字段
# =========================
required_columns = ["Chinese", "Math"]

for column in required_columns:
    if column not in train_data.columns:
        raise ValueError("训练集缺少字段：" + column)

    if column not in test_data.columns:
        raise ValueError("预测集缺少字段：" + column)

print("\n========== 数据基本信息 ==========")

print("训练集规模：", train_data.shape)
print("训练集字段：", train_data.columns.tolist())

print("预测集规模：", test_data.shape)
print("预测集字段：", test_data.columns.tolist())

print("\n训练集前5条数据：")
print(train_data.head())

print("\n预测集前5条数据：")
print(test_data.head())


# =========================
# 4. 检查数据类型
# =========================
print("\n========== 数据类型 ==========")

print("训练集数据类型：")
print(train_data.dtypes)

print("\n预测集数据类型：")
print(test_data.dtypes)


# =========================
# 5. 检查缺失值
# =========================
print("\n========== 缺失值检查 ==========")

print("训练集缺失值：")
print(train_data.isnull().sum())

print("\n预测集缺失值：")
print(test_data.isnull().sum())


# =========================
# 6. 检查重复值
# =========================
print("\n========== 重复值检查 ==========")

print("训练集重复行数量：", train_data.duplicated().sum())
print("预测集重复行数量：", test_data.duplicated().sum())


# =========================
# 7. 检查成绩描述统计
# =========================
print("\n========== 训练集成绩统计 ==========")

print(train_data[required_columns].describe())

print("\n========== 预测集成绩统计 ==========")

print(test_data[required_columns].describe())


# =========================
# 8. 检查异常值（IQR方法）
# 这里只标记，不删除
# =========================
print("\n========== 异常值检查 ==========")

for column in required_columns:
    q1 = train_data[column].quantile(0.25)
    q3 = train_data[column].quantile(0.75)
    iqr = q3 - q1

    lower = q1 - 1.5 * iqr
    upper = q3 + 1.5 * iqr

    outliers = train_data[
        (train_data[column] < lower) |
        (train_data[column] > upper)
    ]

    print(
        column,
        "异常值数量：",
        len(outliers),
        "判断范围：",
        (lower, upper)
    )


# =========================
# 9. 绘制成绩散点图
# =========================
plt.figure(figsize=(8, 6))

plt.scatter(
    train_data["Chinese"],
    train_data["Math"],
    alpha=0.7
)

plt.xlabel("Chinese Score")
plt.ylabel("Math Score")
plt.title("Student Score Distribution")
plt.grid(alpha=0.3)

plt.savefig(
    result_dir / "score_scatter.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()


# =========================
# 10. 绘制成绩分布直方图
# =========================
plt.figure(figsize=(10, 5))

plt.hist(
    train_data["Chinese"],
    bins=10,
    alpha=0.6,
    label="Chinese"
)

plt.hist(
    train_data["Math"],
    bins=10,
    alpha=0.6,
    label="Math"
)

plt.xlabel("Score")
plt.ylabel("Number of Students")
plt.title("Score Histogram")
plt.legend()
plt.grid(alpha=0.3)

plt.savefig(
    result_dir / "score_histogram.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()


# =========================
# 11. 保存统计结果
# =========================
train_data[required_columns].describe().to_csv(
    result_dir / "train_statistics.csv",
    encoding="utf-8-sig"
)

test_data[required_columns].describe().to_csv(
    result_dir / "test_statistics.csv",
    encoding="utf-8-sig"
)

print("\n========== 数据分析完成 ==========")
print("图表和统计结果已保存到 results 文件夹。")
