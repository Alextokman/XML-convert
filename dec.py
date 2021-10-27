i = 82
i = str(bin(i))
i = i[2:]
i = i[::-1]
for c in range(0,11):
    if c < len(i):
        print(i[c])
    else:
        print("0")
