#define _POSIX_C_SOURCE 200112L
#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>

#define NUM_THREADS 4

// shared data between threads
int A[4] = {1, 2, 3, 4};
int B[4] = {0, 0, 1, 1};
int K[4] = {1, 3, 3, 1};
int L[4] = {2, 2, 3, 3};
int R[4] = {4, 4, 4, 4};

pthread_mutex_t lock_x;
//pthread_barrier_t barrier;

void *thread_func(void *arg) {
    int i = *(int*)arg;
    pthread_mutex_lock(&lock_x);
    int z = A[K[i]];
    pthread_mutex_unlock(&lock_x);
    if (B[i] == 0) {
        pthread_mutex_lock(&lock_x);
        A[L[i]] = z + 5;
        A[R[i]] = A[R[i]] + 1;
        pthread_mutex_unlock(&lock_x);
    }
    pthread_exit(NULL);
}

int main(int argc, char **argv) {
    pthread_t thread[NUM_THREADS];
    int thread_data[NUM_THREADS];

    pthread_mutex_init(&lock_x, NULL);
    //pthread_barrier_init(&barrier, NULL, NUM_THREADS);
    

    int return_value;
    for (int i = 0; i < NUM_THREADS; ++i) {
        thread_data[i] = i;
        if ((return_value = pthread_create(&thread[i], NULL, thread_func, &thread_data[i]))) {
            fprintf(stderr, "error: pthread_create, error code: %d\n", return_value);
            return EXIT_FAILURE;
        }
    }

    //wait until all threads complete
    //pthread_barrier_wait(&barrier);
    for(int i = 0; i < NUM_THREADS; ++i) {
        pthread_join(thread[i], NULL);
    }
    
    /*Compare output with serial version*/
    for(int i=0; i<4; ++i){
        printf("%d ", A[i]);
    }

    return EXIT_SUCCESS;
}
