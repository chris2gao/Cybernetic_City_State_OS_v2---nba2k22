import importlib.util,json,sqlite3,sys
connection=sqlite3.connect(':memory:')
try:result={'dbstat_available':True,'probe_rows':connection.execute('SELECT count(*) FROM dbstat').fetchone()[0]}
except sqlite3.OperationalError as error:result={'dbstat_available':False,'reason':str(error)}
print(json.dumps({'python':sys.version.split()[0],'sqlite':sqlite3.sqlite_version,**result,'optional_modules':{name:importlib.util.find_spec(name) is not None for name in ('apsw','pysqlite3')}}))
connection.close()
