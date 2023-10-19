import numpy as np
import random

my_list = [4, 5, 1, 2, 1]

min_value = min(my_list)
min_indices = np.where(np.array(my_list) == min_value)[0]

# if len(min_indices) > 1:
#     # If there are multiple indices with the minimum value, choose randomly
#     chosen_index = random.choice(min_indices)
# else:
#     chosen_index = min_indices[0]

chosen_index = random.choice(min_indices) if len(min_indices) > 1 else min_indices[0]


print(chosen_index)
