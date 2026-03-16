#include <stdio.h>
#include <stdlib.h>

int comp(const void* a,const void* b) {
    return *(int*)a - *(int*)b;
}

int main() {
  int arr[5] = {1, 4, 3, 5, 2};
    int n = sizeof(arr)/sizeof(arr[0]);
  
    qsort(arr, n, sizeof(int), comp);
  
    for (int i = 0; i < n; i++) {
        printf("%d ", arr[i]);
    }
    printf("\n");
    return 0;
}
