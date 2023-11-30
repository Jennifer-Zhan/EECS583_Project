int main() {
    int A[4] = {1, 2, 3, 4};
    #pragma omp parallel for
    for(int i=0; i<4; ++i){
        for(int j=0; j<4; ++j){
            A[i][j] = i+j+1;
        }
    }
    #pragma omp barrier
}