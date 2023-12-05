int main() {
    int A[4] = {1, 2, 3, 4};
    
    int i;

    for (i = 1; i < 4; i++) {
        A[i] = A[i - 1] + 5;
    }

    return 0;
}