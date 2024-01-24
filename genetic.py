import random
from math import ceil

'''def generate_random_individual(items, num_bins, bin_capacity):
    temp_items = items
    random.shuffle(temp_items)
    #print(temp_items)
    bin_load = [0] * num_bins
    j = 0
    encoded_state = []
    for i in range(len(temp_items)):
        # while loop to make sure that each item is placed in a bin
        while True:
            if not valid(bin_load[j], bin_capacity, temp_items[i][0]):
                j += 1
                # to make sure that j will not exceed num_bins value
                j = j % num_bins
                continue
            else:
                bin_load[j] += temp_items[i][0]
                encoded_state.append((temp_items[i],j))
                j += 1
                j = j % num_bins
                break
    #print(bin_load)
    #print(encoded_state)
    random.shuffle(encoded_state)
    return encoded_state
'''


def generate_random_individual(items, num_bins, bin_capacity):  # 4 3 5   [(4,1) ,(3,2) , (5,3)]
                                                        # 0 1 2
    temp_items = items.copy()
    random.shuffle(temp_items)

    bin_load = [0] * len(items)  # 4 3 0  #5   25
    encoded_state = []   #[]

    for item in temp_items:
        while True:
            j = random.randint(0, len(items) - 1)
            if valid_bin(bin_load[j], bin_capacity, item[0]):
                bin_load[j] += item[0]
                encoded_state.append((item, j))  #[((3,2),1) ,(4,1)  , ((5,3),2)]
                                                 #[((3,2),1) , ((4,1),0) , ((5,3),2)]
                break
    return shift_pipes(encoded_state)  # ((2,1),4)


def valid_bin(bin_load, bin_capacity, item):
    return bin_load + item <= bin_capacity


def valid_state(encoded_state, items):
    sum_of_state = 0
    for i in range(len(encoded_state)):
        sum_of_state += encoded_state[i][0][0]

    if sum_of_state == sum(items):
        return True
    else:
        # print("more than inputs")
        return False


def is_valid_bin(encoded, bin_capacity, num_bins):
    # to check if the all bins are valid or no after crossover
    #bin_load = [0] * num_bins
    bin_load = [0] * check_bins_number(encoded)
    for item in encoded:
        if valid_bin(bin_load[item[1]], bin_capacity, item[0][0]):
            bin_load[item[1]] += item[0][0]
        else:
            # print("bin excced capacity")
            return False
    return True


def check_for_exceeded_bins(encoded, num_bins):
    for item in encoded:
        if item[1] >= num_bins:
            # print("more than number of bins")
            return True
    return False


def check_for_redundant_items(encoded):
    check_frequency = {}
    for item in encoded:
        my_pair = (item[0][0], item[0][1])
        # Initialize count to 1 if the key is not present
        check_frequency[my_pair] = check_frequency.get(my_pair, 0) + 1

    for key, value in check_frequency.items():
        if value > 1:
            # print("redundant pair")
            return True
    return False


def evaluate_fitness(encoded, items, num_bins, bin_capacity):
    if check_for_exceeded_bins(encoded, num_bins) or check_for_redundant_items(encoded):
        return 10000

    if is_valid_bin(encoded, bin_capacity, num_bins) and valid_state(encoded, items):
        return check_bins_number(encoded)
    else:
        return 1000











def check_bins_number(encoded):
    distinct_bins = set()
    for item in encoded:
        distinct_bins.add(item[1])
    return len(distinct_bins)


def crossover(parent1, parent2, num_bins, bin_capacity):
    # Create clones of parents
    child1 = parent1.copy()
    child2 = parent2.copy()
    child1 = shift_pipes(child1)       #[(3,1),(5,2)||,(4,3)]  [(3,1),(5,2),(4,3),|||(4,4) ( 5, 6 ) , (8,7,)]
    child2 = shift_pipes(child2)        #( 5, 6 ) , (8,7,) ,(3,1),(5,2)
    # Choose two crossover points per clone
    crossover_point1 = random.randint(1, len(child1) - 1)
    crossover_point2 = random.randint(1, len(child2) - 1)

    # Transfer bins between parents
    child1[crossover_point1:] = parent2[crossover_point1:]
    child2[crossover_point2:] = parent1[crossover_point2:]

    # Perform corrections to make valid solutions
    child1 = remove_duplicates(child1)
    child2 = remove_duplicates(child2)  #[(3,1),(5,2)||,(5,2)]

    # Create lists of unassigned items
    unassigned_items_child1 = get_unassigned_items(parent1, child1)
    unassigned_items_child2 = get_unassigned_items(parent2, child2)

    # shift all pipes to start from 0
    child1 = shift_pipes(child1)
    child2 = shift_pipes(child2)

    # Insert remaining unassigned items
    child1 = insert_unassigned_items(child1, unassigned_items_child1, bin_capacity)
    child2 = insert_unassigned_items(child2, unassigned_items_child2, bin_capacity)

    # shift all pipes to start from 0
    child1 = shift_pipes(child1)
    child2 = shift_pipes(child2)
    return child1, child2


def shift_pipes(chromosome):
    # add distinct bins to a set
    distinct_bins = set()
    for item in chromosome:
        distinct_bins.add(item[1])

    # transfer it to a list and then sort it
    list_of_set = list(distinct_bins)
    list_of_set.sort()

    # map every index to the lowest available index
    idx = 0
    my_map = {}
    for item in list_of_set:
        my_map[item] = idx
        idx += 1
    new_chromosome = []

    # make the chromosome empty and then insert the new shifted list to your chromosome again
    for i in range(len(chromosome)):
        new_chromosome.append((chromosome[i][0], my_map[chromosome[i][1]]))

    return new_chromosome


def remove_duplicates(chromosome):
    seen_items = set()
    new_chromosome = []

    # Remove bins that contain duplicates
    for i in chromosome:
        if i[0] not in seen_items:
            seen_items.add(i[0])
            new_chromosome.append(i)
    return new_chromosome


def get_unassigned_items(parent, child):
    # Create a set of all items in the parent
    all_items = set()
    for i in parent:
        all_items.add(i[0])

    # Create a set of items in the child
    child_items = set()
    for i in child:
        child_items.add(i[0])

    # Return unassigned items (items in the parent but not in the child)
    return list(all_items - child_items)


def calculate_bin_loads(chromosome, bin_capacity):
    bin_loads = [0] * check_bins_number(chromosome)
    for i in range(len(chromosome)):
        if valid_bin(bin_loads[chromosome[i][1]], bin_capacity, chromosome[i][0][0]):
            bin_loads[chromosome[i][1]] += chromosome[i][0][0]
    return bin_loads


def insert_unassigned_items(chromosome, unassigned_items, bin_capacity):
    # Sort unassigned items by size in descending order
    unassigned_items.sort(reverse=True)
    bin_loads = calculate_bin_loads(chromosome, bin_capacity)

    # Try to insert the item into the first bin with enough free space
    for i in range(len(unassigned_items)):
        flag = False
        j = 0
        while j < check_bins_number(chromosome):
            if valid_bin(bin_loads[j], bin_capacity, unassigned_items[i][0]):
                bin_loads[j] += unassigned_items[i][0]
                chromosome.append((unassigned_items[i], j))
                flag = True
                break
            j += 1
        # If no bin has enough space, create a new bin
        if flag is False:
            chromosome.append((unassigned_items[i], j))
            bin_loads.append(0)
            bin_loads[j] += unassigned_items[i][0]

    return chromosome


def mutate(encoded, num_bins, bin_capacity):
    mutated = encoded.copy()
    for i in range(3):
        mutated.remove(mutated[random.randint(0, len(mutated)-1)])
    mutated = shift_pipes(mutated)
    unassigned = get_unassigned_items(encoded, mutated)
    mutated = insert_unassigned_items(mutated, unassigned, bin_capacity)
    return mutated


'''

if __name__ == "__main__":
    # Take number of bins and bin capacity as input
    num_bins = int(input("Enter the number of bins: "))
    bin_capacity = int(input("Enter the bin capacity: "))

    # Take item sizes as input
    item_sizes = [int(size) for size in input("Enter item sizes separated by spaces: ").split()]
    item_sizes_pairs = [(size, i) for i, size in enumerate(item_sizes)]
    population_size = 100
    num_generations = 100

    genetic_algorithm(population_size,num_generations,item_sizes_pairs,item_sizes,num_bins,bin_capacity)
'''
