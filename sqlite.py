import sqlite3

conn = sqlite3.connect("Student.db")

cursor = conn.cursor()

table = """
CREATE TABLE STUDENT(
    NAME VARCHAR(25),
    BRANCH VARCHAR(25),
    SECTION VARCHAR(10),
    MARKS INT
)
"""
cursor.execute(table)

cursor.execute(''' Insert into STUDENT values('A','AI','B','98')''')
cursor.execute(''' Insert into STUDENT values('B','DS','C','96')''')
cursor.execute(''' Insert into STUDENT values('C','ME','D','95')''')
cursor.execute(''' Insert into STUDENT values('D','ECE','E','94')''')
cursor.execute(''' Insert into STUDENT values('E','CSE','A','93')''')
cursor.execute(''' Insert into STUDENT values('F','AIML','B','92')''')
cursor.execute(''' Insert into STUDENT values('G','CIVIL','D','91')''')


print("Inserted Records Of students are: ")
data = cursor.execute(''' Select * from STUDENT''')

for row in data:
    print(row)

conn.commit()
conn.close()