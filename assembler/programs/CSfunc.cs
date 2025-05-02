// programs/CSfunc.cs

// A simple helper function with one parameter
void Foo(int z) {
    // declare a new variable and do a + operation
    int t = z + 2;
}

/*
    This is a
    multiline comment
    spanning several lines.
    It will be skipped entirely by our lexer.
*/

// Entry point
int Main() {
    // variable declarations + assignment
    int a = 10;
    int b = 3;
    int c = a + b;

    // reassignment with a - operation
    a = c - 1;

    // if/else with a comparison
    if (a >= b) {
        Foo(a);
    } else {
        Foo(b);
    }

    // while loop
    while (b < a) {
        b = b + 1;
    }

    // return a value
    return b;
}
