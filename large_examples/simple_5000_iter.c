int main() {
    int A[1000] = {0};
    
    int i;

    for (i = 0; i < 5000; i++) {
        A[i] = A[i] + 5;
    }

    return 0;
}