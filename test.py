import numpy as np
# Example 1: Use numpy.append() function
arr = np.array([[0,2,4],[6,8,10]]) 
app_arr = np.append(arr, [13,15,17]) 
print(app_arr)

# Example 2: Appending array with axis=0
arr = np.array([[0,2,4],[6,8,10]]) 
app_arr=np.append(arr, [[5,7,9],[13,15,17]],axis = 0)
print(app_arr)

# Example 3: Use Append elements along axis 1
arr = np.array([[0,2,4],[6,8,10]]) 
app_arr=np.append(arr, [[5,7,9],[13,15,17]],axis = 1) 
print(app_arr)

# Example 4: Use appending array
arr = np.arange(7)  
arr1 = np.arange(9, 14)
arr2 = np.append(arr, arr1)
print("Appended arr2 : ", arr2)
