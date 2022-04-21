def get_atom(which):
    atom = input("What is the {} atom?".format(which))
    try:
        return int(atom)
    except:
        print("Please enter a number.")
        return get_atom(which)


lines_lists = []
lines_list = []
atom1 = get_atom("first")
atom2 = get_atom("second")
count_lines_to_skip = True
lines_to_skip = 0
filename = input("What is your xyz file name?")
with open("{}.xyz".format(filename), "r") as xyzfile:
    for line in xyzfile:
        lines_list.append(line)
        if len(line.split()) == 4:
            count_lines_to_skip = False
        elif count_lines_to_skip:
            lines_to_skip += 1
        if (
            len(line.split()) != 4
            and not count_lines_to_skip
            and len(lines_list) > lines_to_skip
        ):
            last_line = lines_list.pop()
            lines_lists.append(lines_list)
            lines_list = [last_line]
    lines_lists.append(lines_list)

with open("{}_{}_{}.xyz".format(filename, atom1, atom2), "w") as newfile:
    for lines in lines_lists:
        atom1_line = lines[atom1 + lines_to_skip - 1]
        atom2_line = lines[atom2 + lines_to_skip - 1]
        lines[atom2 + lines_to_skip - 1] = atom1_line
        lines[atom1 + lines_to_skip - 1] = atom2_line
        for line in lines:
            newfile.write(line)
