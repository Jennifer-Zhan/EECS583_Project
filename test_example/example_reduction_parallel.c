int main() {
    int A[4] = {1, 2, 3, 4};
    int sum = 0;
    #pragma omp parallel for
    for(int i=0; i<4; ++i){
        #pragma omp critical {
        sum += A[i];
        }
    }
    #pragma omp barrier
    for(int i=0; i<4; ++i){
        print(A[i])
    }
}