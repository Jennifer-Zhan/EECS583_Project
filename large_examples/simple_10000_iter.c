int main() {
    int A[10000] = {0};
    
    int i;

    for (i = 0; i < 1000; i++) {
        A[i] = A[i] + 5;
    }

    return 0;
}