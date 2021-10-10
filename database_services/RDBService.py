import pymysql
import json
import logging
import middleware.context as context

# region logger
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()
logger.setLevel(logging.INFO)
# endregion

from pypika import Query, Table, Parameter

# region DB name
DB_SCHEMA = "Stonk"
DB_USER_TABLE = "User"
# region

def debug(func):
    def wrapper(*args, **kwargs):
        print(f"Args: {args} {kwargs}" )
        out = func(*args, **kwargs)
        print(f"Output: {out}")
        return out
    return wrapper

def _get_db_connection():
    db_connect_info = context.get_db_info()

    logger.debug("RDBService._get_db_connection:")
    logger.debug("\t HOST = " + db_connect_info['host'])

    db_info = context.get_db_info()
    db_connection = pymysql.connect(
        **db_info
    )
    return db_connection

def insert_new_record(db_schema, table_name, record, return_primary_key = False):
    """

    :param db_schema:
    :param table_name:
    :param dict records: new record to insert, expressing using dictionary (for each dict item: key -> column name, value -> value for that column)
    :param bool return_primary_key: if set to true, return primaryKey, else return None
    :return: if return_primary_key is set to true, return primaryKey, else return None
    """

    conn = _get_db_connection()
    cur = conn.cursor()

    #string for generating sql query string
    col_str = "("
    # string for generating sql query string
    val_str = "("
    # value for sql query
    val = []
    for r in record:
        col_str += (r + ", ")
        val_str += ("%s" + ", ")
        val.append(record[r])
    col_str = col_str[:-2]
    col_str += ")"
    val_str = val_str[:-2]
    val_str += ")"

    #logger.debug(col_str)
    #logger.debug(val_str)
    #logger.debug(val)

    sql = "INSERT INTO " + db_schema + "." + table_name + " " + col_str + " " \
                                                           "VALUES " + val_str + ";"
    #logger.debug(sql)

    logger.debug("SQL Statement = " + cur.mogrify(sql, val))
    res = cur.execute(sql, val) #safe way to avoid SQL Injection
    conn.commit()
    primary_key = None
    if return_primary_key:
        primary_key = cur.execute("SELECT LAST_INSERT_ID()")
        primary_key = cur.fetchall()
        logger.debug("New Record Primary Key Value:" + str( primary_key[0]['LAST_INSERT_ID()']))

    conn.close()
    if return_primary_key:
        return primary_key[0]['LAST_INSERT_ID()']

def run_sql(func):
    def wrapper(*args, **kwargs):
        sql, values = func(*args, **kwargs)

        conn = _get_db_connection()
        cur = conn.cursor()

        logger.debug("SQL Statement = " + cur.mogrify(sql, values))
        cur.execute(sql, values)  # safe way to avoid SQL Injection
        res = cur.fetchall()
        conn.commit()
        conn.close()
        logger.debug("SQL Success")
        return res
    wrapper.__name__ = func.__name__
    return wrapper


@run_sql
def remove_old_record(db_schema, table_name, primary_key, key_value):
    return f"DELETE FROM {db_schema}.{table_name} WHERE {primary_key}=%s;", key_value

@run_sql
@debug
def update_record_with_keys(db_schema, table_name, keys, record):
    """

    :param db_schema: database_schema
    :param table_name: table_name
    :param dict keys:  dict for primary keys and its value
    :param record: records for update
    :return:
    """

    tbl = Table(f'{db_schema}.{table_name}')
    query, values = Query.update(tbl), []

    for k in record.keys():
        query = query.set(tbl[k], Parameter('%s'))
    values.extend(record.values())

    for k in keys.keys():
        query = query.where(tbl[k] == Parameter('%s'))
    values.extend(keys.values())

    return str(query).replace("\"", ''), values

    conn = _get_db_connection()
    cur = conn.cursor()

    condition_str = "";

    for p in keys:
        condition_str += (p + " = '" + keys[p] + "' AND ")
    condition_str = condition_str[:-5]
    #print(condition_str)

    record_column_str = "";
    record_values = []
    for r in record:
        record_column_str += (r + " = %s, ")
        record_values.append(record[r])
    record_column_str = record_column_str[:-2]
    #print(record_column_str)
    #print(record_values)

    sql = "UPDATE " + db_schema + "." + table_name + " SET " + record_column_str + " WHERE " + condition_str + ";";
    logger.debug("SQL Statement = " + cur.mogrify(sql, record_values))
    res = cur.execute(sql, record_values)  # safe way to avoid SQL Injection
    conn.commit()
    conn.close()
    logger.debug("Update Success")

@run_sql
@debug
def get_by_template(db_schema, table_name, keys = None, fields = None):
    tbl = Table(f'{db_schema}.{table_name}')
    query = Query.from_(tbl)
    values = []

    if fields is None or len(fields) == 0:
        query = query.select('*')
    else:
        values.extend(fields)
        query = query.select( *[Parameter('%s') * len(fields)] )

    for k, v in keys.items():
        values.append(v)
        query = query.where(tbl[k] == Parameter('%s'))

    return str(query).replace("\"", ""), values



    conn = _get_db_connection()
    cur = conn.cursor()

    stmt = cur.mogrify(str(query).replace("\"", ''))
    print(f"get_by_template(), SQL Statement = {stmt}")
    cur.execute(stmt)
    res = cur.fetchall()

    conn.close()
    return res