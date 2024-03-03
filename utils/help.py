def GetHelp():
    file_path = 'utils/commands/commands.txt'
    with open(file_path, 'r') as file:
        content = file.readlines()
    output = "\n\n".join(line for line in content)
    return output