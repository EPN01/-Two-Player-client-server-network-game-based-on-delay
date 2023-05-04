import socket  #Eric
import time 
import random
import tabulate
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((socket.gethostname(), 8000))

number_of_connections = 2 #number of players, can be set to any number
server.listen(number_of_connections)
score=0 

print('Server is listening and ready for connections')
#create seperate lists, one for the current round, and one for the cumulative rounds, one for clients, and one for the rtt times to be compared
players_cum_rounds=[]
players=[]
client=[]
times=[]
player_number=1

try:
    while len(players) < number_of_connections:
        clientsock, address = server.accept()
        print('Connection from', address)
        clientsock.send(f'Welcome, you are now connected to the game!\nYou are player {player_number}'.encode())
        
        # see if here or after both are connected
        players.append([clientsock,score,f"Player {player_number}"])
        players_cum_rounds.append([clientsock,score,f"Player {player_number}"])
        # this is the part of the code that lets the server wait for players to join, and once
        # the players join, it stops the loop and moves on to start the game
        client.append(clientsock)
        player_number+=1
except Exception as e:
    print("The following error has occured, please try again later:\n")
    print(e)
    server.close()

try:
    for round in range(1,4): # 3 rounds numbered 1,2,3  #Lama
        print('\nRound ',round)
        for i in range(len(players)): # for each player
            players[i][1]=0 # reset their score to 0
            times=[] # reset their time to -1
        number=random.randint(0,9) # random number between 0 and 9
        for i in range(number_of_connections):
            client[i].send(str(number).encode()) # send the number to player i
            time1=time.time() # start the timer
            while True:
                client_number = client[i].recv(1024)

                if  client_number.decode()==str(number):
                    RTT=time.time()-time1 # calculate the RTT
                    times.append([RTT,i])
                    break
                elif client_number.decode()=='timeout': #if timeout, player is disqualified
                    print(f"Player {i+1} took too long to guess, they are disqualified from this round!\n")
                    break
                elif client_number.decode()!=str(number) or client_number.decode()=='empty': # wrong guess or no guess (empty string)
                    print(f"Player {i+1} guessed wrong, they are disqualified from this round!\n")
                    break
               
        tie=False
        if times==[]: tie=True	#Antoine
        else: 
            times.sort(key=lambda x: x[0]) # sort the times by their RTT (ascending)
            players[times[0][1]][1]+=1 # add 1 to the score of the player with the lowest RTT
            players_cum_rounds[times[0][1]][1]+=1 # add 1 to the cumulative score of the player with the lowest RTT
        current_round=sorted(players, key=lambda x: x[1]) # sort the players by their score 
        current_round.reverse()
        cumulative_score=sorted(players_cum_rounds, key=lambda x: x[1]) # sort the players by their cumulative score 
        cumulative_score.reverse()

        if not tie: print('\nThe winner of this round is',current_round[0][2])
        else: print("\nThis round ended in a tie, no players got a point!")
        table = [["Players", "Score", "Cumulative Score"]] # print the scores after each round in a table, with headings as seen
        for i in range(number_of_connections):
            j=0
            while j<number_of_connections: #this is to find the player in current_round list that corresponds to the player in cumulative_score list [i]
                if current_round[j][2]==cumulative_score[i][2]: break
                j+=1 
            table.append([cumulative_score[i][2], current_round[j][1], cumulative_score[i][1]]) #creating the table
        tempstring = str(tabulate.tabulate(table, headers='firstrow', tablefmt='fancy_grid'))
        print(tempstring) 
        for ff in client:#send table to client as a string
            ff.send((tempstring+"table").encode()) #we added 'table' so the client knows it received a table

    if cumulative_score[0][1]==0: # if no one got a point, all disqualifications
        print('\nNo one won the game!')  
        for i in range(number_of_connections):#send to everyone that noone won
            cumulative_score[i][0].send(("Unfortunately, No One Won the Game!!").encode())  

    elif cumulative_score[0][1]!=cumulative_score[1][1]: 
        print('\nThe winner of the game is',cumulative_score[0][2])#send to winner that they won
        cumulative_score[0][0].send(("Congratulations, you have won the game!!").encode())
        for i in range(1,number_of_connections):#send to everyone else that they lost
            cumulative_score[i][0].send(("Sorry, you lost the game!!").encode())

    elif number_of_connections>2 and cumulative_score[1][1]==cumulative_score[2][1]: #at most 3 way tie since 3 rounds
        print(f'\nThe game ended in a three way tie!, the winners are, {cumulative_score[0][2]}, {cumulative_score[1][2]}, and {cumulative_score[2][2]}')
        for i in range(number_of_connections):
            if i<3:#send to the three people who tied that they tied
                cumulative_score[i][0].send(("Congratulations, you were part of the threeway tie").encode())
            else:#send to everyone else that they lost
                cumulative_score[i][0].send(("Sorry, you lost the game").encode())

    else:
        print(f'\nThe game ended in a tie! The winners are, {cumulative_score[0][2]} and {cumulative_score[1][2]}')
        for i in range(number_of_connections):
            if i<2:#send to the two people who tied that they tied
                cumulative_score[i][0].send(("Congratulations, you were part of the two-way tie").encode())
            else:#send to everyone else that they lost
                cumulative_score[i][0].send(("Sorry, you lost the game").encode())


except socket.error as e: #handles socket disconnections  #Eric
    print("The following error has occured; ")
    for p in players: #find the player who disconnected, i is from the loops above where the disconnection happened, thus i is the client that disconnected
        if p[0] == client[i]:
            c=p[2]
    strin=f"{c} has disconnected, the game will now end"
    for x in client:#send to everyone that a player has disconnected, and the specific player that disconnected
        if x != client[i]:
            x.send((strin).encode())
    print(strin)


except Exception as e:
    print("The following error has occured, please try again later:")
    print(e)
    
server.close()
