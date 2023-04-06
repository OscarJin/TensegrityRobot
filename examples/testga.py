import src.TensegrityModel.tensegrity_ga as GA

ga = GA.TensegGA(strut_num=4)
p1 = ga.create_individual()
print(p1)
p2 = ga.create_individual()
ch1, ch2 = ga.crossover(p1, p2)
ga.mutate(p1)
print(p1)
