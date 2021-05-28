import os

in_file = [filename for filename in os.listdir('./')
           if filename.startswith('draw_f')]
for filename in in_file:
    with open(filename, 'r', encoding='utf-8') as f:
        hist = []
        lines = f.readlines()
        for line in lines:
            line = line.rstrip()[1:-1].split(', ')
            x = int(line[1])
            y = int(line[2])
            if [x, y] in hist:
                print(filename, 'Wrong', line)
            hist.append([x, y])
            if line[1] == line[2] or len(line) < 4:
                print(filename, 'Wrong', line)
in_file = [filename for filename in os.listdir('./')
           if filename.startswith('dot_f')]
for filename in in_file:
    with open(filename, 'r', encoding='utf-8') as f:
        hist = []
        lines = f.readlines()
        for line in lines:
            line = line.rstrip()[1:-1].split(', ')
            x = float(line[1])
            y = float(line[2])
            if [x, y] in hist:
                print(filename, 'Wrong', line)
            hist.append([x, y])
