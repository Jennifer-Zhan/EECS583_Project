int main() {
    int A[20000] = {0};
    
    int i;

    for (i = 0; i < 30000; i++) {
        A[i] = A[i] + 5;
    }

    return 0;
}