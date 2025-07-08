import os
import ydb
import json
import random

YDB_ENDPOINT = os.getenv("YDB_ENDPOINT")
YDB_DATABASE = os.getenv("YDB_DATABASE")

def get_ydb_pool(ydb_endpoint, ydb_database, timeout=30):
    ydb_driver_config = ydb.DriverConfig(
        ydb_endpoint,
        ydb_database,
        credentials=ydb.credentials_from_env_variables(),
        root_certificates=ydb.load_ydb_root_certificate(),
    )

    ydb_driver = ydb.Driver(ydb_driver_config)
    ydb_driver.wait(fail_fast=True, timeout=timeout)
    return ydb.SessionPool(ydb_driver)


def _format_kwargs(kwargs):
    return {"${}".format(key): value for key, value in kwargs.items()}


# Заготовки из документации
# https://ydb.tech/en/docs/reference/ydb-sdk/example/python/#param-prepared-queries
def execute_update_query(pool, query, **kwargs):
    def callee(session):
        prepared_query = session.prepare(query)
        session.transaction(ydb.SerializableReadWrite()).execute(
            prepared_query, _format_kwargs(kwargs), commit_tx=True
        )

    return pool.retry_operation_sync(callee)


# Заготовки из документации
# https://ydb.tech/en/docs/reference/ydb-sdk/example/python/#param-prepared-queries
def execute_select_query(pool, query, **kwargs):
    def callee(session):
        prepared_query = session.prepare(query)
        result_sets = session.transaction(ydb.SerializableReadWrite()).execute(
            prepared_query, _format_kwargs(kwargs), commit_tx=True
        )
        return result_sets[0].rows

    return pool.retry_operation_sync(callee)    

# Зададим настройки базы данных 
pool = get_ydb_pool(YDB_ENDPOINT, YDB_DATABASE)

async def load_quiz_data():
    query = """
        SELECT id, question, options, correct_index
        FROM quiz_questions;
    """
    rows = execute_select_query(pool,query)

    questions = [
        {
            "question": row["question"],
            "options": json.loads(row["options"]),
            "correct_option": row["correct_index"]
        }
        for row in rows
    ]
    random.shuffle(questions)
    return questions

def get_score(user_id: int) -> int:
    query = """
    DECLARE $user_id AS Uint64;
    SELECT score FROM quiz_state
    WHERE user_id = $user_id;
    """
    rows = execute_select_query(pool, query, user_id=user_id)
    return rows[0].score if rows and rows[0].score is not None else 0

def update_score(user_id: int, new_score: int):
    query = """
        DECLARE $user_id AS Uint64;
        DECLARE $score AS Int32;
        UPDATE quiz_state
        SET score = $score
        WHERE user_id = $user_id;
    """
    execute_update_query(
        pool, query, 
        user_id=user_id, 
        score=new_score
    )

def reset_quiz_state(user_id: int) -> None:
    query = """
        DECLARE $user_id AS Uint64;
        DECLARE $question_index AS Int32;
        DECLARE $score AS Int32;
        REPLACE INTO quiz_state (user_id, question_index, score)
        VALUES ($user_id, $question_index, $score);
    """
    execute_update_query(
        pool, query,
        user_id=user_id,
        question_index=0,
        score=0
    )

# Структура квиза
# quiz_data = [
#     {
#         'question': 'Что такое Python?',
#         'options': ['Язык программирования', 'Тип данных', 'Музыкальный инструмент', 'Змея на английском'],
#         'correct_option': 0
#     },
#     {
#         'question': 'Какой тип данных используется для хранения целых чисел?',
#         'options': ['int', 'float', 'str', 'natural'],
#         'correct_option': 0
#     },
#     # Добавьте другие вопросы
# ]
