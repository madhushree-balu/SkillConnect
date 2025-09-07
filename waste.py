arr = list(map(int, input().split()))

c = 0

for i in range(1, len(arr) - 1):
    if arr[i+1] + arr[i-1] == arr[i]:
        c += 1
        
print(c)