mylist = [
            {'user': 'Bot1', 'version': 0.11, 'items': 23, 'methods': 'standard', 'time': 1536304833437, 'logs': 'no', 'status': 'completed'},
            {'user': 'Bot2', 'version': 0.15, 'items': 43, 'methods': 'standard', 'time': 2555645896453, 'logs': 'yes', 'status': 'cancelled'},
            {'user': 'Bot3', 'version': 0.17, 'items': 63, 'methods': 'standard', 'time': 3265114687998, 'logs': 'yes', 'status': 'completed'}
          ]

for mydict in mylist:
    placeholders = ', '.join(['%s'] * len(mydict))
    columns = ', '.join("`" + str(x).replace('/', '_') + "`" for x in mydict.keys())
    values = ', '.join("'" + str(x).replace('/', '_') + "'" for x in mydict.values())
    sql = "INSERT INTO %s ( %s ) VALUES ( %s );" % ('mytable', columns, values)
    print(sql)