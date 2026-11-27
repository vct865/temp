
import os
import pymysql
import pandas as pd


# 数据库配置
DB_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "242424",
    "charset": "utf8mb4"
}

DATABASE_NAME = "student_group"


def get_connection():
    """连接数据库"""
    return pymysql.connect(
        **DB_CONFIG,
        database=DATABASE_NAME
    )


def create_database():
    """创建数据库"""
    connection = pymysql.connect(**DB_CONFIG)

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                f"CREATE DATABASE IF NOT EXISTS `{DATABASE_NAME}` "
                "DEFAULT CHARACTER SET utf8mb4"
            )
        connection.commit()
        print("数据库创建成功！")
    finally:
        connection.close()


def create_table():
    """创建学生群体数据表"""
    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            sql = """
                CREATE TABLE IF NOT EXISTS student_groups (
                    sno BIGINT PRIMARY KEY,
                    Chinese FLOAT NOT NULL,
                    Math FLOAT NOT NULL,
                    cluster INT NOT NULL,
                    `group` VARCHAR(50) NOT NULL
                )
            """
            cursor.execute(sql)

        connection.commit()
        print("数据表创建成功！")
    finally:
        connection.close()


def import_data():
    """批量导入或更新预测结果"""
    file_path = os.path.join(
        os.path.dirname(__file__),
        "results",
        "predict_result.csv"
    )

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"找不到文件：{file_path}")

    df = pd.read_csv(file_path)

    required_columns = [
        "sno", "Chinese", "Math", "cluster", "group"
    ]

    if not all(column in df.columns for column in required_columns):
        raise ValueError("预测结果文件缺少必要字段！")

    data = [
        (
            int(row["sno"]),
            float(row["Chinese"]),
            float(row["Math"]),
            int(row["cluster"]),
            str(row["group"])
        )
        for row in df[required_columns].to_dict("records")
    ]

    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            sql = """
                INSERT INTO student_groups
                (sno, Chinese, Math, cluster, `group`)
                VALUES (%s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    Chinese = VALUES(Chinese),
                    Math = VALUES(Math),
                    cluster = VALUES(cluster),
                    `group` = VALUES(`group`)
            """

            cursor.executemany(sql, data)

        connection.commit()
        print(f"成功导入或更新 {len(data)} 条学生记录！")
    finally:
        connection.close()


def query_by_sno(sno):
    """按学生编号查询"""
    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            sql = """
                SELECT sno, Chinese, Math, cluster, `group`
                FROM student_groups
                WHERE sno = %s
            """
            cursor.execute(sql, (sno,))
            return cursor.fetchone()
    finally:
        connection.close()


def query_by_group(group):
    """按群体标签查询"""
    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            sql = """
                SELECT sno, Chinese, Math, cluster, `group`
                FROM student_groups
                WHERE `group` = %s
                ORDER BY sno
            """
            cursor.execute(sql, (group,))
            return cursor.fetchall()
    finally:
        connection.close()


if __name__ == "__main__":
    create_database()
    create_table()
    import_data()

    print("\n========== 按学生编号查询 ==========")
    result = query_by_sno(10001)
    print(result if result else "没有找到该学生")

    print("\n========== 按群体标签查询 ==========")
    results = query_by_group("优秀发展型")
    print(f"共查询到 {len(results)} 人")

    for row in results:
        print(row)
