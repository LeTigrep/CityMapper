f = open("combined.csv", 'r')

next(f)

next_L1 = f.readline()
while next_L1 != "":
    items = next_L1.rstrip("\n").split(";")
    f2 = items[5].split(",")

    for row in f2:
        f3 = row.split(":")
        print(f"INSERT INTO combined_TABLE VALUES (\'{items[0]}\', \'{items[1]}\', \'{items[2]}\', \'{float(items[3])/60.0}\', \'{f3[0]}\', \'{items[6]}\');") 
    next_L1 = f.readline()
