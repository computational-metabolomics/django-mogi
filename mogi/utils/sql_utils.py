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


def filterset_to_sql_stmt(filterset):
    filters = filterset.filters
    print(filters.keys())
    sql_filters = []
    for row in filterset.data.items():
        print(row)
        if row[0] in filters.keys() and row[1]:
            sql_filters.append(filter_to_sql_stmt(row[0], row[1]))

    if sql_filters:
        return ' AND ' + ' AND '.join(sql_filters)
    else:
        return ''



def filter_to_sql_stmt(d_filter, val):
    colnm, comp = d_filter.split('__')

    if comp == 'gt':
        comp_sql_compat = '>'
        return '{} {} {}'.format(colnm, comp_sql_compat, val)
    elif comp == 'lt':
        comp_sql_compat = '<'
        return '{} {} {}'.format(colnm, comp_sql_compat, val)
    elif comp == 'contains':
        comp_sql_compat = 'LIKE'
        return '{} {} "%{}%"'.format(colnm, comp_sql_compat, val)

