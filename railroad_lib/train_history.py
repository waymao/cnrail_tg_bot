import pymysql
import bot_config

# id from num
def get_train_id(train_no):
    sql = '''SELECT trainNumber AS train_no, 
                    railNo AS train_id, 
                    trainType AS train_type,
                    queryTime AS train_date,
                    Company AS company
            FROM trainlog
            WHERE trainNumber LIKE \"{}\" 
            ORDER BY queryTime DESC LIMIT 2;
    '''.format(train_no)
    return mysql_get_result(sql)


# train id to checi (no)
def get_train_no_wo_type(train_id):
    sql = '''SELECT trainNumber AS train_no, 
                    railNo AS train_id, 
                    trainType AS train_type,
                    queryTime AS train_date,
                    Company AS company
            FROM trainlog
            WHERE railNo = \"{}\"
            ORDER BY queryTime DESC LIMIT 1;
    '''.format(train_id)
    return mysql_get_result(sql)


# train id plus type to checi (no)
def get_train_no_w_type(train_id, train_type):
    sql = '''SELECT trainNumber AS train_no, 
                    railNo AS train_id, 
                    trainType AS train_type,
                    queryTime AS train_date,
                    Company AS company
            FROM trainlog
            WHERE railNo = \"{}\" AND
                    trainType = \"{}\"
            ORDER BY queryTime DESC LIMIT 1;
    '''.format(train_id, train_type)
    return mysql_get_result(sql)


# general mysql query helper function.
def mysql_get_result(sql):
    mysql_cred = bot_config.mysql_info
    connection = pymysql.connect(host=mysql_cred['host'],
                                user=mysql_cred['user'],
                                password=mysql_cred['password'],
                                db=mysql_cred['db'],
                                charset='utf8mb4',
                                cursorclass=pymysql.cursors.DictCursor)
    try:
        with connection.cursor() as cursor:
            cursor.execute(sql)
            result = cursor.fetchall()
    finally:
        connection.close()
    return result
