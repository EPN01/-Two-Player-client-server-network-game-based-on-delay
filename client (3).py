import socket  #Elias
import os
import inputimeout

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
client.connect(( socket.gethostname(), 8000))
os.system("cls") #clear the screen in the command prompt

welcome = client.recv(1024).decode()
print(welcome)
error=False
for round in range(1,4):
    p=c=''
    print("Round ",round)
    number = client.recv(1024).decode()
    if len(number)==1: #to check if it is not a number, something went wrong, such as client disconnecting
        print("The number is: ",number)
        try:
            guess=inputimeout.inputimeout("Guess the number: ",timeout=10)
        except inputimeout.TimeoutOccurred:
            c="You took too long to guess, you are disqualified from this round!"
            print(c)
            guess="timeout"
        else:
            if guess!=number: # if the guess is wrong, client is disqualified
                p="Wrong guess, you are disqualified from this round!"
                print(p)

        if guess=="": #if guess is empty set guess to empty to be able to handle it at the server side
            guess = "empty"
        client.send(guess.encode())
        table = client.recv(1024).decode()
        os.system("cls") #clear the screen in the command prompt
        if table[-5:]=="table": # to ensure we received the table, since we added a code to the end of the table in the server before sending
            print(welcome)
            # the following statements are used to tell the players that they were disqualified or timed out the previous round, if they were
            if p!="": print("\n"+"You guessed wrong last round, and were disqualified from that round!") #if p not empty, then player had guessed wrong
            if c!="": print("\n"+"You took too long to guess last round, and were disqualified from that round!") #if c not empty, then player had timed out
            print('\n'+table[:-5])
        else:
            print("An error has occured; ") # if we received something else, something went wrong, thus its an error
            print("\n"+table) #table is the error already received from the server
            client.close()
            error=True
            break
    else:
        print("An error has occured; ") # if we received something other than a number, something went wrong, thus its an error
        print("\n"+number) #number is the error already received from the server
        client.close()
        error=True
        break
if not error: # if no error occured, we can receive the final message from the servers
    msg = client.recv(1024).decode()
    print("\n"+msg)
    client.close()

