f = open("nodes.csv", 'r', encoding='UTF-8')

next(f)

for line in f:
    items = line.rstrip("\n").split(";") 
    
    print(f"INSERT INTO nodes_TABLE VALUES (\'{items[0]}\'", end='')

    for item in items[1:] :
        item = item.replace("'", "''")
        if(item != ''):
            print(f", \'{item}\'" ,end='')
         
    print(");")

  



