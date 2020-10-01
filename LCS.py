import numpy as np

#Used to calculate the longest common subsequence between 2 words
class LCS:
    def __init__(self, word_x, word_y):
        self.word_x = word_x
        self.word_y = word_y
        self.T = np.zeros((len(word_x)+1, len(word_y)+1))



    def get_LCS(self):
        self.T = np.zeros((len(self.word_x)+1, len(self.word_y)+1))
        result = self.lcs(len(self.word_x), len(self.word_y))

        return result

    def lcs(self, i, j):
        if i*j == 0:
            return 0
        elif self.word_x[i-1] == self.word_y[j-1]:
            self.T[i, j] = self.lcs(i-1, j-1) + 1
            return self.T[i, j]
        else:
            self.T[i, j] = max(self.lcs(i-1, j), self.lcs(i, j-1))
            return self.T[i, j]


