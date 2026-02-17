from __future__ import print_function
from django.db import connection
from sqlite3 import OperationalError


def insert_query_m(data, table, columns=None):

    if len(data)>10000:
        chunk_query(data, 10000, columns, table)
    else:
        type = "%s, " * (len(data[0]) - 1)
        type = type + "%s"

        if columns:
            stmt = "INSERT INTO " + table + "( " + columns + ") VALUES (" + type + ")"
        else:
            stmt = "INSERT INTO " + table + " VALUES (" + type + ")"

        print(stmt)

        cursor = connection.cursor()
        cursor.executemany(stmt, data)
        connection.commit()


def chunk_query(l, n, cn, name):
    # For item i in a range that is a length of l,
    [insert_query_m(l[i:i+n], name, cn) for i in range(0, len(l), n)]


def sql_query(query):
    with connection.cursor() as cursor:
        cursor.execute(query)
        columns = [i[0] for i in cursor.description]
        rows = cursor.fetchall()

    return rows, columns


def get_current_row(model):
    # get last id of LipidSearchSampleGroup
    m = model.objects.filter().order_by('-id')
    if m:
        id = m[0].id + 1
    else:
        id = 1

    return id



def select_query(stmt):

    cursor = connection.cursor()
    cursor.execute(stmt)
    connection.commit()
    return [i for i in cursor]


def sql_column_names(cursor):
    names = {}
    c = 0
    for description in cursor.description:
        names[description[0]] = c
        c += 1

    return names

def check_table_exists_sqlite(cursor, tablename):
    #https://stackoverflow.com/questions/17044259/python-how-to-check-if-table-exists
    try:
        qry =cursor.execute("SELECT NULL FROM {} LIMIT 1".format(tablename))
    except OperationalError as e:
        return False

    return True


def filterset_to_sql_stmt(filterset, field_sql_map=None):
    if not filterset:
        return ''

    filterset.form.is_valid()

    sql_filters = []
    cleaned_data = getattr(filterset.form, 'cleaned_data', {})
    for filter_name, value in cleaned_data.items():
        if value in (None, ''):
            continue

        filter_obj = filterset.filters.get(filter_name)
        if not filter_obj:
            continue

        if getattr(filter_obj, 'method', None):
            continue

        column_name = filter_obj.field_name
        if field_sql_map:
            mapped_column_name = field_sql_map.get(filter_name) or field_sql_map.get(column_name)
            if mapped_column_name:
                column_name = mapped_column_name

        lookup_expr = filter_obj.lookup_expr
        sql_stmt = filter_to_sql_stmt(column_name, value, lookup_expr)
        if sql_stmt:
            sql_filters.append(sql_stmt)

    if sql_filters:
        return ' AND ' + ' AND '.join(sql_filters)
    else:
        return ''


def filter_to_sql_stmt(column_name, value, lookup_expr):
    if lookup_expr == 'gt':
        return '{} > {}'.format(column_name, value)
    elif lookup_expr == 'lt':
        return '{} < {}'.format(column_name, value)
    elif lookup_expr == 'contains':
        escaped_value = str(value).replace('"', '""').replace("'", "''")
        return "{} LIKE '%{}%'".format(column_name, escaped_value)
    elif lookup_expr == 'exact':
        if isinstance(value, bool):
            return '{} = {}'.format(column_name, 1 if value else 0)
        elif isinstance(value, (int, float)):
            return '{} = {}'.format(column_name, value)
        else:
            escaped_value = str(value).replace('"', '""').replace("'", "''")
            return "{} = '{}'".format(column_name, escaped_value)
    return ''

