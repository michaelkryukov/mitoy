# mitoy

> Toy interpreted programming language

A little language written in my spare time with `python` and `rply`. It's
nothing special or serious, but I decided to share anyway. I received some
nice experience that can help me in future projects (maybe one day I will
create worthy programming language \_c:_/).

You can find language's grammar in [this file](grammar). Example programs and
their test you can find in [this folder](examples/).

## Example program

```mitoy
import t "testing"

fn Fact(n) {
    if n < 1 { ret 1 };
    ret n * Fact(n - 1);
}

# Function will be called when testing
fn Test() {
    t.Describe("Factorial function", fn (Case) {
        Case("!0 should be equal to 1", fn (Test) {
            Test(Fact(0)).ToBeEqual(1);
        });

        Case("Fact should return correct values", fn (Test) {
            Test(Fact(4)).ToBeEqual(24);
            Test(Fact(5)).ToBeEqual(120);
        });
    });
}

# Function will be called when calling file directly
fn Main() {
    TraceNl(Fact(4));  # Outputs 24
    TraceNl(Fact(5));  # Outputs 120
}
```

## Running

```bash
python3 -m pip install -r requirements.txt

python3 mitoy 'path/to/program.mitoy' # run application
python3 mitoy --test 'path/to/folder' # run tests for every file in folder
```

## Notes

- This project probably won't be developed further
