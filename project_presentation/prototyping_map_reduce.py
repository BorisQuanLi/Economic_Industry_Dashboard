a = (1, 2, 3, 4)
b = (5, 6, 7, 8)
d = (10, 11, 12, 13)
c= [a, b]

# https://realpython.com/python-itertools/
inputs = [1, 2, 3, 4, 5, 6]
num = 2
n = 2
master_list = []
breakpoint()
numb_iterations = int(len(inputs) / n)
for i in range(numb_iterations):
    master_list.append(tuple(inputs[i*n:(i+1)*n]))
print (master_list)
breakpoint()
    


# https://stackoverflow.com/questions/44193736/explanation-on-unpacking-a-list-with-itertools-product
print(((x,y) for x in a for y in b))

print(list((x,y) for x in a for y in b))
breakpoint()

def sum_elements_two_lists(list1, list2):
    return [tupl[0] + tupl[1] for tupl in zip(list1, list2)]


print(f"from sum_elements_two_lists function: {sum_elements_two_lists(a, b)}")

from functools import reduce

# print(reduce(lambda x, y: sum_elements_two_lists(x, y), [a, b, c]))
#print(reduce(lambda x, y: [list(x)[i] + list(y)[i] for i in range(len(x))], [a, b, c]))

combined_list = []
for tup in zip(a, b, d):
    element_sum = sum([tup[i] for i in range(3)])
    combined_list.append(element_sum)
print(f"combined_list: {combined_list}")

print(list(map(lambda x: sum([x[i] for i in range(3)]), zip(a,b,d))))
print('Result from reduce(): \n')
print(list(reduce(lambda x, y: (tup[0] + tup[1]
                                    for tup in zip(x, y)), [a, b, d])))
print(reduce(lambda x, y: [tup[0] + tup[1]
                                    for tup in zip(x, y)], [a, b, d]))

companies_pe_history_list = [20.51, 22.98, 21.93, 23.27]

print(reduce(lambda x, y: [tup[0] + tup[1] for tup in zip(x,y)], 
            companies_pe_history_list) 
                if type(companies_pe_history_list[0]) == tuple 
                                else companies_pe_history_list)

print(list(map(lambda x: x/3, [16, 19, 22, 25])))