import datetime
import random

last = ""
i = 0
while i < 20:
    number = random.randrange(100)
    if (number % 2) == 0:
        numtype = "even"
        print("{0} is Even".format(number))
    else:
        numtype = "odd"
        print("{0} is Odd".format(number))
    if last == numtype:
        print("same")
    else:
        print(numtype)

    last = numtype


    i = i + 1








