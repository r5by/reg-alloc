int foo(int n) {
    int z = 10;
    int x = 0;
    int y = 1;

    while(x < n) {
        z = x * 2 + y;
        x++;
        y = x + z;
    }

    return y;
}