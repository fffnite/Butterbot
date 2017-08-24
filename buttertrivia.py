import os
import operator
from os import walk, listdir, remove
from random import randint


current_trivia = []
index = 0
score = {}


#Opens the given trivia and loads all the questions/answers
def set_trivia(trivia):
    file_open = open("triviagames/{}.txt".format(trivia.lower()), "r")
    
    #.txt format = "":"","","" per rad
    for line in file_open:
        result_tup = (line.split(":")[0], line.split(":")[1].strip().lower().split(","))
        current_trivia.append(result_tup) 
    file_open.close()


#Gets all files in dir triviagames with the file ending .txt
#then splits each file on . and capitalizes it so we only get
#the filenames capitalized. We then return a list of these filenames
def get_trivias_list():
    return [ str(f).split(".")[0].capitalize()
             for f in listdir("triviagames") 
             if f.endswith(".txt") ]


#Returns all trivias as an output string to be viewed in discord.
def get_trivias():
    f = get_trivias_list()
    result = "There is currently " + str(len(f)) + " games:\n"
    result += '\n'.join(f)#e.split(".")[0].capitalize() for e in f)
    return result


#Checks if the given trivia exists
def search_trivias(trivia):
    f = get_trivias_list()
    return True if trivia.capitalize() in get_trivias_list() else False



def load_trivia(trivia):
    return ("Successfully started trivia: " + trivia.capitalize() 
            if search_trivias(trivia) 
            else "There is no trivia with name: " + trivia.capitalize())


#Randomize a number between 0 and end of list, then return the 
#question on the randomed numbers index in the question list
def get_question():
    global current_trivia, index
    index = randint(0,len(current_trivia)-1)
    return current_trivia[index][0]


#If length of list is larger than index there is more questions
#if not we are done
def check_if_more_questions():
    global current_trivia
    return len(current_trivia) > 0


#Removes the current question
def delete_question():
    global current_trivia, index
    del current_trivia[index]


#Checks if the provided answer is an answer in the answer list
#if it is we remove the question from the list and return True
#for a correct answer.
#If the answer is not correct we return false.
def check_answer(answer):
    global current_trivia, index
    try:
        if answer.lower() in current_trivia[index][1]:
            del current_trivia[index]
            return True
        else:
            return False
    except IndexError:
        return False


#Gives the provided person +1 in score
def give_score(person):
    global score
    score[person] = score[person] + 1 if person in score else 1


#Prints the score for everyone who has atleast got 1 answer corrrect
def print_score():
    global score
    return "\n".join("{} has score: {}".format(k, v) for k, v in score.items())


#Gets the highest person(s) in the scorelist as winner for the trivia
#game
def get_winner():
    global score
    winner = ""
    prev_val = 0
    for k,v in score.items():
        if prev_val <= v:
            if prev_val == v:
                winner += ", " + k
            else:
                prev_val = v
                winner = k
    score = {}
    return winner


#Ends the current triviagame
def exit_trivia():
    global current_trivia, index, score
    current_trivia = []
    score = {}
    return False


#Get the highscore
def get_highscore():
    highscore = "Trivia highscore:\n"
    files = open("highscore.txt", "r")
    highscore +=  "".join(line.split(":")[0] + " : " + line.split(":")[1] for line in files)
    return highscore
    #for line in files:
    #    highscore += line.split(":")[0] +" : " + line.split(":")[1]
    #return highscore


#Update the highscore based on the last played trivia
def update_highscore():
    global score
    file_list = []
    files = open("highscore.txt", "r")
    highscore = { line.split(":")[0]: int(line.split(":")[1]) for line in files }
    files.close()

    open("highscore.txt", "w").close()
    files = open("highscore.txt", "w")
    
    highscore = { k: ( int(highscore[k]) if k in highscore else 0 ) + v 
                  for k,v in score.items() }
    print("Highscore dict built")
    print(highscore)
    #for k,v in score.items():
    #    if k not in highscore:
    #        highscore[k] = 0
    #    val = highscore[k]
    #    highscore[k] = int(val) + v
    
    highscore = sorted(highscore.items(), key=operator.itemgetter(1))
    highscore.reverse()
    print("Sorted highscore:")
    print(highscore)
    files.writelines([ str(tup[0]) + ":" + str(tup[1]) + "\n" for tup in highscore ])
    #for tup in highscore:
    #    file_list.append(str(tup[0]) + ":" + str(tup[1]) + "\n")
    #files.writelines(file_list)
    files.close()


#Add a question to a trivia, if the trivia doesnt exist, create it 
#and put that question in it.
def add_question(trivia, question, answers):
    result = ""
    result += question + ":"
    answers = answers[0].split(" ")
    
    result += ",".join(answers)
    print("Result with answers")
    print(result)
    result += "\n"
    with open("triviagames/" + trivia.lower() + ".txt", "a") as files:
        files.write(result)


#Lists all questions for a given trivia
def list_questions(trivia):
    if search_trivias(trivia.lower()):
        files_read = open("triviagames/" + trivia.lower() + ".txt", "r")
        result = "All questions in " + trivia.capitalize() + "\n"
        questions = [ line for line in files_read ]
        files_read.close()
        result += "\n".join("{}. {}".format(i, question.split(":")[0]) 
                            for i, question in enumerate(questions))
        if questions == []:
            result = "There is currently no questions in trivia " + trivia.capitalize()
    else:
        result = "There is no trivia with name " + trivia.capitalize()
    return result


#Removes a question on the provided trivia on the provided index
#Get the index from list_questions
def remove_question(trivia, question_nr):
    if search_trivias(trivia.lower()):
        files_read = open("triviagames/" + trivia.lower() + ".txt", "r")
        questions = [ line for line in files_read ]
        try:
            del questions[int(question_nr)]
        except IndexError:
            return "Invalid index for trivia " + trivia.capitalize()
        files_read.close()

        open("triviagames/" + trivia.lower() + ".txt", "w").close()

        files_write = open("triviagames/" + trivia.lower() + ".txt", "w")
        files_write.writelines(questions)
        files_write.close()
        return "Successfully removed question " + question_nr + " from trivia " + trivia.capitalize()
    else:
        return "There is no trivia named " + trivia.capitalize()


#Removes the trivia
def remove_trivia(trivia):
    try:
        os.remove("triviagames/" + trivia.lower() + ".txt")
        return True
    except OSError:
        return False
