# -*- coding: utf-8 -*-

import numpy as np
import math 
import copy
import re
import time

NOIR = -1
BLANC = 1


class Pion:
    
    def __init__(self, ligne, col, couleur):
        self.dame = False
        self.ligne = ligne
        self.col = col
        self.couleur = couleur
    
    def devientDame(self):
        self.dame = True
    
    def getPos(self):
        return (self.ligne,self.col)
    
    def setPos(self, pos):
        self.ligne = pos[0]
        self.col = pos[1]
        
    def __repr__(self):
        if self.couleur == NOIR:
            if self.dame:
                return "\u2655"
            return "\u25CB"
        else:
            if self.dame:
                return "\u265B"
            return "\u25CF"

        
class Game:
    
    def __init__(self):
        self.plateau = []
        
        for ligne in range(8):
            self.plateau.append([])
            for col in range(8):
                if col % 2 == ((ligne +  1) % 2):
                    if ligne < 3:
                        self.plateau[ligne].append(Pion(ligne, col, BLANC))
                    elif ligne > 4:
                        self.plateau[ligne].append(Pion(ligne, col, NOIR))
                    else:
                        self.plateau[ligne].append(0)
                else:
                    self.plateau[ligne].append(0)
        
        self.nb_noir = self.nb_blanc = 12
        self.nb_dame_noire = self.nb_dame_blanche = 0
        self.jouer = 0
        self.cpt = 0
        self.profondeur = 4
    
    def affichage(self, plateau):
        print("\n   0   1   2   3   4   5   6   7")
        print(" +-------------------------------+")
        for ligne in range(len(plateau)):
            l = str(ligne)+"|"
            for col in range(len(plateau[ligne])):
                if isinstance(plateau[ligne][col], Pion):
                    l += " "+str(plateau[ligne][col])+" |"
                else:
                    l += "   |"
            print(l)
            if ligne < 7:
                print(" ---------------------------------")
        print(" +-------------------------------+\n")
    
    def affichagePossibilite(self, move):
        pion_deplace = move[0]
        i, j = pion_deplace.getPos()
        plateau = move[1]
        print("\n   0   1   2   3   4   5   6   7")
        print(" +-------------------------------+")
        for ligne in range(len(plateau)):
            l = str(ligne)+"|"
            for col in range(len(plateau[ligne])):
                if isinstance(plateau[ligne][col], Pion):
                    if ligne == i and col == j:
                        l += " \033[1;32m"+str(plateau[ligne][col])+"\033[1;37m |"
                    else:
                        l += " "+str(plateau[ligne][col])+" |"
                else:
                    l += "   |"
            print(l)
            if ligne < 7:
                print(" ---------------------------------")
        print(" +-------------------------------+\n")

    def checkFinDePartie(self, couleur):
        gagnant = 0
        if self.nb_noir <= 0 and self.nb_dame_noire <= 0:
            gagnant = BLANC
        elif self.nb_blanc <= 0 and self.nb_dame_blanche <= 0:
            gagnant = NOIR
        partie_finie = True
        for ligne in range(len(self.plateau)):
            for col in range(len(self.plateau[ligne])):
                pion = self.plateau[ligne][col]
                if isinstance(pion, Pion):
                    if pion.couleur == couleur:
                        if self.seDeplacer(pion, self.plateau) != [] or \
                                self.manger(pion, self.plateau) != []:
                            partie_finie = False
        return (partie_finie, gagnant)
    

    
    def seDeplacer(self, pion, plateau):        
        couleur = pion.couleur
        x, y = pion.getPos()
        if pion.dame:
            movesPot = [(x+couleur, y-1), (x+couleur, y+1), (x-couleur, y-1), (x-couleur, y+1)]
        else:
            movesPot = [(x+couleur, y-1), (x+couleur, y+1)]
        liste_plateau = []
        moves = [(i,j) for (i,j) in movesPot if i < 8 and i >= 0 and 
                         j >= 0 and j < 8 and plateau[i][j] == 0]
        for i, j in moves:
            plateau_new = copy.deepcopy(plateau)
            new_pion = plateau_new[x][y]
            plateau_new[i][j] = new_pion
            new_pion.setPos((i,j))
            plateau_new[x][y] = 0
            liste_plateau.append((new_pion, plateau_new))
        return liste_plateau
    
    def manger(self, pion, plateau):
        couleur = pion.couleur
        x, y = pion.getPos()
        if pion.dame:
            movesPot = [(x+couleur*2, y-2), (x+couleur*2, y+2), (x-couleur*2, y-2), (x-couleur*2, y+2)]
        else:
            movesPot = [(x+couleur*2, y-2), (x+couleur*2, y+2)]
        moves = []
        liste_plateau = []
        for i, j in movesPot:
            if i < 8 and i >= 0 and j >= 0 and j < 8 and plateau[i][j] == 0:
                if isinstance(plateau[(x + i)//2][(y + j)//2], Pion):
                    if plateau[(x + i)//2][(y + j)//2].couleur == -couleur:
                        moves.append((i,j))
        for i, j in moves:
            plateau_new = copy.deepcopy(plateau)
            new_pion = plateau_new[x][y]
            plateau_new[i][j] = new_pion
            new_pion.setPos((i,j))
            plateau_new[x][y] = 0
            plateau_new[(x + i)//2][(y + j)//2] = 0
            liste_plateau.append((new_pion, plateau_new))
            liste_plateau += self.manger(new_pion,plateau_new)
        return liste_plateau
    
    def getMovePion(self, pion, plateau):
        moves = []
        couleur = pion.couleur
        moves += self.seDeplacer(pion, plateau)
        moves += self.manger(pion, plateau)
        return moves
    
    def effectuerMove(self, move):
        self.plateau = move
        cpt_pion_blanc = 0
        cpt_dame_blanc = 0
        cpt_pion_noir = 0
        cpt_dame_noir = 0
        for ligne in move:
            for p in ligne:
                if isinstance(p, Pion):
                    if p.couleur == NOIR:
                        cpt_pion_noir += 1
                        if p.ligne == 0:
                            p.dame = True
                            cpt_dame_noir += 1
                            cpt_pion_noir -= 1
                    else:
                        cpt_pion_blanc += 1
                        if p.ligne == 7:
                            p.dame = True
                            cpt_dame_blanc += 1
                            cpt_pion_blanc -= 1
        self.nb_noir = cpt_pion_noir
        self.nb_blanc = cpt_pion_blanc
        self.nb_dame_noire = cpt_dame_noir
        self.nb_dame_blanche = cpt_dame_blanc
        self.affichage(self.plateau)
        
    def getAllPion(self, plateau, couleur):
        liste_pion = []
        for ligne in plateau:
            for p in ligne:
                if isinstance(p, Pion):
                    if p.couleur == couleur:
                        liste_pion.append(p)
        return liste_pion
    
    def takeSecond(elem):
        return elem[1]
    
    def getAllMoves(self, plateau, couleur):
        liste_pion = self.getAllPion(plateau, couleur)
        moves = []
        for pion in liste_pion:
            moves += self.getMovePion(pion, plateau)
        moves.sort(key=lambda x: self.evaluate(x[1], x[0].couleur),reverse=True)

        return moves    
    
    def evaluate(self, plateau, couleur):
        result = 0
        pion_blanc = 0
        pion_blanc_dame = 0
        pion_noir = 0
        pion_noir_dame = 0
        for i in range(len(plateau)):
            for j in range(len(plateau[i])):
                if isinstance(plateau[i][j], Pion):
                    if plateau[i][j].couleur == BLANC:
                        pion_blanc += 1
                        if plateau[i][j].dame:
                            pion_blanc_dame += 1
                    elif plateau[i][j].couleur == NOIR:
                        pion_noir += 1
                        if plateau[i][j].dame:
                            pion_noir_dame += 1
        if couleur == NOIR:
            return (pion_noir - pion_blanc) + (pion_noir_dame * 0.5 - pion_blanc_dame * 0.5 )
        else:
            return (pion_blanc - pion_noir) + (pion_blanc_dame * 0.5 - pion_noir_dame * 0.5 )
    
    def minimax(self, plateau, depth, maximizingPlayer):        
        if depth == 0 or self.checkFinDePartie()[0]:
            return self.evaluate(plateau, couleur), plateau
        
        if maximizingPlayer:
            maxEval = -math.inf
            bestMove = None
            
            allmoves = self.getAllMoves(plateau, BLANC)
            for move in allmoves:
                evaluation = self.minimax(move[1], depth-1, False)[0]
                maxEval = max(maxEval, evaluation)
                if maxEval == evaluation:
                    bestMove = move[1]
            return maxEval, bestMove
        else:
            minEval = math.inf
            bestMove = None
            
            allmoves = self.getAllMoves(plateau, NOIR)
            for move in allmoves:
                evaluation = self.minimax(move[1], depth-1, True)[0]
                minEval = min(minEval, evaluation)
                if minEval == evaluation:
                    bestMove = move[1]
            return minEval, bestMove
        
    def alphabeta(self, plateau, depth, alpha, beta, maximizingPlayer, couleur):
        if depth == 0 or self.checkFinDePartie(couleur)[0]:
            return self.evaluate(plateau, couleur)

        if maximizingPlayer:
            maxEval = -math.inf
            
            allmoves = self.getAllMoves(plateau, couleur)
            for move in allmoves:
                self.cpt += 1
                evaluation = self.alphabeta(move[1], depth-1, alpha, beta, False, couleur)
                maxEval = max(maxEval, evaluation)
                alpha = max(alpha, evaluation)
                if beta <= alpha:
                    break
            return maxEval
        else:
            minEval = math.inf
            
            allmoves = self.getAllMoves(plateau, -couleur)
            for move in allmoves:
                self.cpt += 1
                evaluation = self.alphabeta(move[1], depth-1, alpha, beta, True, couleur)
                minEval = min(minEval, evaluation)
                beta = min(beta, evaluation)
                if beta <= alpha:
                    break
            return minEval
    
    def choisirPion(self):
        bon_pion = False
        while not bon_pion:
            
            pos = input("Choisissez le pion à bouger. Exemple: 5,0 \n")
            if re.search("^[\d],[\d]$", pos):
                pos = pos.split(',')
                x = int(pos[0])
                y = int(pos[1])
                if x < 8 and x >= 0 and y >= 0 and y < 8:
                    pion = self.plateau[x][y]
                    if isinstance(pion, Pion):
                        if pion.couleur == NOIR:
                           bon_pion = True
                        else:
                           print("Le pion selectionné ne fait pas partie des votre.") 
                    else:
                        print("La case selectionnée ne contient pas de pion.")
                else:
                    print("La position du pion que vous souhaitez n'existe pas.")
            else:
                print("Mauvaise entrée ! Veuillez recommencer.")
        return self.plateau[x][y]
    
    def tourJoueur(self):
        self.affichage(self.plateau)
        pasVide = False
        while not pasVide:
            pion = self.choisirPion()
            moves = self.getMovePion(pion, self.plateau)
            if moves != []:
                pasVide = True
            else:
                print("Pas de mouvement de disponible pour ce pion.")
        for i in range(len(moves)):
                print("\n"+str(i)+":")
                self.affichagePossibilite(moves[i])
        bon_move = False
        while not bon_move:
            index_mouvement = input("Choisissez le coup à jouer. Exemple: 0 \n")
            if re.search("^[\d]$", index_mouvement):
                index_mouvement = int(index_mouvement)
                if index_mouvement in range(len(moves)):
                    bon_move = True
                else:
                    print("Ce mouvement n\'est pas disponible.")
            else:
                print("Mauvaise entrée ! Veuillez recommencer.")
        self.effectuerMove(moves[index_mouvement][1])
    
    def tourBot(self, couleur):
        if couleur == NOIR:
            print("Le bot noir joue son tour ...")
        else:
            print("Le bot blanc joue son tour ...")
        """
        value, move = self.minimax(self.plateau, 4, True)
        self.effectuerMove(move)
        """
        self.cpt = 1
        temps1 = time.time()
        value = self.alphabeta(self.plateau, self.profondeur, -math.inf, math.inf, True, couleur)
        print("Score AlphaBeta : "+str(value))
        child = {}
        allmoves = self.getAllMoves(self.plateau, couleur)
        for move in allmoves:
            child[self.alphabeta(move[1], self.profondeur-1, -math.inf, math.inf, False, couleur)] = move[1]
        temps2 = time.time()
        print("Temps d\'execution: "+str(temps2 - temps1))
        print("Nombre de noeuds parcourus: "+str(self.cpt))
        print("Score heuristique: "+str(self.evaluate(self.plateau,couleur)))
        self.effectuerMove(child[value])
    
    def lancerGame(self):
        print("Voulez-vous jouer contre le bot ou regarder une partie ?")
        correct = False
        while not correct:
            jouer = input("Tapez 1 pour jouer contre le bot ou 2 pour regarder une partie \n")
            if re.search("^[\d]$", jouer):
                jouer = int(jouer)
                correct = True
            else:
                print("Mauvaise entrée !")
        while not self.checkFinDePartie(BLANC)[0] and not self.checkFinDePartie(NOIR)[0]:
            if jouer == 1:
                self.tourJoueur()
                self.tourBot(BLANC)
            else:
                self.tourBot(NOIR)
                time.sleep(2)
                self.tourBot(BLANC)
                time.sleep(2)
        result = self.checkFinDePartie(NOIR)[1]
        if result == NOIR:
            print("Les noirs ont gagné !")
        elif result == BLANC:
            print("Les blancs ont gagné !")
        else:
            print("Partie nulle !")
        
if __name__ == '__main__':
    game = Game()
    game.lancerGame()
    