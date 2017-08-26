import sys

def trivia_parser(file):
    result = ""
    for line in file:
        result += line.split("`")[0] + "$" + ",".join(line.split("`")[1:])
    return result

if __name__ == "__main__":
    file_to_parse = open(sys.argv[1], "r")
    file_parsed = trivia_parser(file_to_parse)
    file_to_parse.close()
    file_save = open(sys.argv[1], "w")
    file_save.write(file_parsed)
    file_save.close()

