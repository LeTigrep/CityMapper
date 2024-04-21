f = open("routeINT.csv", 'r')
next(f)

for line in f:
    items = line.rstrip("\n").split(";") 
    print(f"INSERT INTO routeINT_TABLE VALUES (\'{items[0]}\', \'{items[1]}\', \'{items[2]}\'", end='')
    print(");")



