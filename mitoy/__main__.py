from parser import parse
import sys
import os

if sys.argv[1] == "--test":
    def test_folder(path):
        for p in os.listdir(path):
            source_path = os.path.join(path, p)

            if os.path.isdir(source_path):
                test_folder(source_path)

            with open(source_path) as fh:
                module = parse(fh.read(), source_path)

                if 'Test' not in module.context:
                    continue

                module.run('Test')

    if os.path.isdir(sys.argv[2]):
        test_folder(sys.argv[2])
    else:
        with open(sys.argv[2]) as fh:
            module = parse(fh.read(), sys.argv[2])
            module.run('Test')

else:
    with open(sys.argv[1]) as fh:
        module = parse(fh.read(), sys.argv[1])
        module.run('Main')
