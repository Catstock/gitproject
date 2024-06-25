import sqlite3

# 连接到数据库
conn = sqlite3.connect('database.db')

# 创建游标
cursor = conn.cursor()

# 删除现有的logs表
cursor.execute('DROP TABLE IF EXISTS logs')

# 创建新的logs表
cursor.execute('''
    CREATE TABLE logs (
      log_no INTEGER PRIMARY KEY AUTOINCREMENT,
      pa_no INTEGER REFERENCES patient(pa_no) ON DELETE CASCADE,
      log_date TEXT DEFAULT (DATE('now', 'localtime')),
      wrong_num INTEGER,
      sum_num INTEGER,
      acc INTEGER,
      score INTEGER
    )
''')

# 提交更改并关闭游标和连接
conn.commit()
cursor.close()
conn.close()
