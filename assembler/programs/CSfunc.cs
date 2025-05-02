void Foo(int z) {
    int t = z + 2;
}


void Main() {
    int a = 10;
    int b = 3;
    int c = a + b;

    a = c - 1;

    if (a >= b) {
        Foo(a);
    } else {
        Foo(b);
    }

    while (b < a) {
        b = b + 1;
    }

    return b;
}
