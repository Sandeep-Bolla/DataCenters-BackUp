
from itertools import combinations
from collections import deque
from sys import maxint, argv, exit
import socket
import subprocess

full_dc_id = str(socket.gethostname())
dc_id = full_dc_id[2:]
backup_dc_id = 0
_fileLocation = None
_fileName = None
_MTX=0
_n=0
_backup = None


# Delimit the output of the program by a hyphen so that the GUI program
# can separate the values. Give provision to store the final results
delimiter = '\n-'
finalResult = None

def takingFileInput():
    global _fileName,_fileLocation
    print"Give the File Name..."
    _fileName = raw_input()
    print"File Location"
    _fileLocation = raw_input()
    if(_fileLocation[-1] != '/'):
	_fileLocation +='/'
    (out, err)= run_cmd(['hadoop', 'fs', '-put', str(_fileLocation)+str(_fileName), '/myFiles'])
    print(err)
    print(out)


def takingNetworkInput():
    global _n,_MTX
    print "How Many Data Centers?"
    _n= int(raw_input())
    print "Now, give the hop-counts of each pair..."
    print
    _MTX= [[0 for i in range(_n)] for j in range(_n)] 
    
    for i in range(_n):
        for j in range(i+1,_n):
	    print "Between"+str(i+1)+" and "+str(j+1)+ ":"
            _MTX[i][j]=int(raw_input())
            _MTX[j][i]=_MTX[i][j]
    
    for i in range(_n):
        _MTX[i][i] = 10000


class color:
   PURPLE = '\033[95m'
   CYAN = '\033[96m'
   DARKCYAN = '\033[36m'
   BLUE = '\033[94m'
   GREEN = '\033[92m'
   YELLOW = '\033[93m'
   RED = '\033[91m'
   BOLD = '\033[1m'
   UNDERLINE = '\033[4m'
   END = '\033[0m'


class HorzLine:
    """Denotes a horizontal line across the matrix"""

    def __init__(self, pos):
        self.finalResult = None
        self.pos = pos
        self.type = "Horizontal"
        self.across = "row"

    def __repr__(self):
        return 'H%d' % (self.pos)


class VertLine:
    """Denotes a vertical line across the matrix"""

    def __init__(self, pos):
        self.pos = pos
        self.type = "Vertical"
        self.across = "column"

    def __repr__(self):
        return 'V%d' % (self.pos)

#Main Class
class HungarianAssignment:
    """A class that solves the HungarianAssignment problem"""

    def __init__(self):
        self.row, self.col, self.M = 0, 0, None
        self.Z = None

    def printMatrix(self):
        print
        for i in self.M:
            for j in i:
                print ' ', j, ' ',
            print
        print delimiter

    def reduceMatrix(self):
        """Returns a row and column reduced matrix"""
        for i in xrange(self.row):
            minElem = min(self.M[i])
            self.M[i] = map(lambda x: x - minElem, self.M[i])

        # Now for column reduction
        for col in xrange(self.row):
            l = []
            for row in xrange(self.row):
                l.append(self.M[row][col])
            minElem = min(l)
            for row in xrange(self.row):
                self.M[row][col] -= minElem

    def getZeroPositions(self):
        """Returns current positions of 0s"""
        self.Z = set()
        for i in xrange(self.row):
            for j in xrange(self.row):
                if self.M[i][j] == 0:
                    self.Z.add((i, j))

    def printZeroLocations(self):
        print '\n Zeros are located at follows:\n\n',
        for i in self.Z:
            print i
        print delimiter

    #Important Method
    def checkAssignments(self):
        """What is the minimum assignment possible to cover all zeros"""
        global _backup, backup_dc_id

        bestComb = self.getSetOfCrossingLines()
        len_BC = len(bestComb)
	backup_id = 0
        print '\n Current best combination covering all zeros: %d\n' % (len_BC)
        for i in bestComb:
            print '\t%s line through %s : %d\n' % (i.type, i.across, i.pos)
        print delimiter

        curAssignments, totalVal = self.getAssignment(), 0
        print '\n  The assignments are as follows: \n\n',
        for i in curAssignments:
            x, y = i[0], i[1]
            print '\t At: ', x, y, ' Value: ',  _backup[x][y], '\n'
            totalVal += _backup[x][y]

        if len(bestComb) != self.row:
            # Perform the following steps
            print '\n Current solution isn\'t optimal: lines are not enough\n'
            print delimiter
            self.tickRowsAndColumns(curAssignments)

        else:
            #self.finalResult = '\n  Optimal assignments are as follows: \n\n'
            print '\n Current solution is optimal: Minimal cost: ', totalVal
            print delimiter
            print '\n Final Results are as Follows\n'
	    print '\t Produciton DC \t Backup DC\n\n',
            for i in curAssignments:
                x, y = int(i[0]), int(i[1])
                print '\t ', x+1,'\t\t',y+1,'\t\t','Hop Cunt',  _backup[x][y], '\n'
		if (x==(int(dc_id)-1)):
		    backup_dc_id = y+1
		    print backup_dc_id
	    return


    def getSetOfCrossingLines(self):
        """Returns a set of lines that minimally cover all zeros"""

        horzLines = [HorzLine(i) for i in xrange(self.row)]
        vertLines = [VertLine(i) for i in xrange(self.row)]
        # We have to choose maximum n lines for crossing out all zeros
        # The assignment is optimal when the minimal lines are the order of the
        # matrix
        allComb, bestComb = [], []
        for i in xrange(1, self.row + 1):
            allComb.extend(combinations(horzLines + vertLines, i))

        # Find the combination which covers the lists in the minimumLines
        for i in allComb:
            covered = set()
            for j in i:
                for zero in self.Z:
                    if zero in covered:
                        continue
                    elif j.type == 'Horizontal' and j.pos == zero[0]:
                        covered.add(zero)
                    elif j.type == 'Vertical' and j.pos == zero[1]:
                        covered.add(zero)
            if len(covered) == len(self.Z):
                if bestComb == []:
                    bestComb = i
                elif len(i) < len(bestComb):
                    bestComb = i

        return bestComb

    def getAssignment(self):
        """Asssign maximum number of zeroes possible """
        removedSet = set()

        # As there can be max n zeros
        bestAssign = set()

        # Since there are atleast 4 zeroes in our zeroes, array
        for comb in combinations(self.Z, self.row):
            removedSet = set()
            totalSet = set(comb)
            curAssign = set()
            for j in totalSet:
                if j in removedSet:
                    continue
                r, c = j[0], j[1]
                # remove others has same row/col
                curAssign.add(j)
                for k in totalSet:
                    if k != j and k not in removedSet:
                        if k[0] == r or k[1] == c:
                            removedSet.add(k)
            if len(curAssign) > len(bestAssign):
                bestAssign = curAssign.copy()
        return bestAssign

    def tickRowsAndColumns(self, assignments):
        """Tick rows and columns in the Matrix accordingly:
        - Tick rows that do not have an assignment
        - Tick cols that have 0's in the marked row
            - Tick all rows that have assignments in the marked column
            - Repeat the above procedure till no more can be ticked
            QuickThink: Use BFS and sets for row/cols
        """
        global _backup
        tickRows, tickCols = set(xrange(self.row)), set()
        # Tick rows without assignment
        for i in assignments:
            curRow = i[0]
            if curRow in tickRows:
                tickRows.remove(curRow)

        queue = deque(tickRows)
        while queue:
            # Tick cols that have 0's in ticked row
            queue.popleft()
            for row in tickRows:
                for col in xrange(self.row):
                    if self.M[row][col] == 0:
                        tickCols.add(col)

            for col in tickCols:
                for assign in assignments:
                    if assign[1] == col and assign[0] not in tickRows:
                        tickRows.add(assign[0])
                        queue.append(assign[0])

        print '\n Ticked rows:  ', list(tickRows)
        print ' Ticked cols:  ', list(tickCols)

        # Draw straight lines through unmarked rows and marked columns
        horLines = [HorzLine(i) for i in xrange(self.row) if i not in tickRows]
        verLines = [VertLine(i) for i in xrange(self.row) if i in tickCols]
        bestComb = horLines + verLines

        print '\n Marking unmarked rows & marked cols:  ', len(bestComb), '\n'
        for i in bestComb:
            print '\t%s line through %s : %d' % (i.type, i.across, i.pos)
        print delimiter

        if horLines + verLines == self.row:
            print '\n Current solution is optimal\n'
            curAssignments, totalVal = self.getAssignment(), 0
            print '\n  The assignments are as follows: \n\n',
            self.finalResult = '\n Optimal assignments are as follows: \n\n'
            for i in curAssignments:
                x, y = i[0], i[1]
                print '\t At: ', x, y, ' Value: ',  _backup[x][y], '\n'
                self.finalResult += '\t At: %d %d \tValue: %d\n\n' % (
                    x, y, _backup[x][y])
                totalVal += _backup[x][y]
            self.finalResult += '\n\n Minimum cost incurred: %d\n ' % (
                totalVal)
            print delimiter
            return True
        else:
            print '\n Current solution isn\'t optimal : lines aren\'t enough\n'
            print ' Now going for uncovering elements pass\n\n'
            self.smallestElements(bestComb)
            self.getZeroPositions()
            self.printZeroLocations()
            self.checkAssignments()

    def smallestElements(self, bestComb):
        """
        Examine uncovered elements: Select min uncovered and subtract from all
        uncovered elements. For elements at intersection of two lines,
        add the min element, for rest : as it is
        """
        H_MASK, V_MASK, I_MASK = "H", "V", "I"
        MASK = [[None for i in xrange(self.row)] for j in xrange(self.row)]

        for line in bestComb:
            if line.type == "Horizontal":
                row = line.pos
                for col in xrange(self.row):
                    if MASK[row][col] is None:
                        MASK[row][col] = H_MASK
                    elif MASK[row][col] == V_MASK:
                        MASK[row][col] = I_MASK

            elif line.type == "Vertical":
                col = line.pos
                for row in xrange(self.row):
                    if MASK[row][col] is None:
                        MASK[row][col] = V_MASK
                    elif MASK[row][col] == H_MASK:
                        MASK[row][col] = I_MASK

        minElem = maxint
        for i in xrange(self.row):
            for j in xrange(self.row):
                if MASK[i][j] == None:
                    minElem = min(minElem, self.M[i][j])
        # Subtract min from uncovered, and add to intersection elems
        for i in xrange(self.row):
            for j in xrange(self.row):
                if MASK[i][j] == None:
                    self.M[i][j] -= minElem
                elif MASK[i][j] == I_MASK:
                    self.M[i][j] += minElem

        print '\n Uncovered matrix\n',
        self.printMatrix()


def readInput():
    """Read matrix from file and return a HungarianAssignment object"""
    solver = HungarianAssignment()

    if len(argv) != 2:
        print '\n No input file feeded'
        print ' Usage: python assignment.py "name_of_InputFile"'
        return solver

    try:
        inputFile = argv[1]
        f = file(inputFile, "r")
        n, m = map(int, f.readline().strip().split(" "))
        _n = n
        M = [[-1 for a in xrange(_n)]
             for b in xrange(_n)]  # denotes the matrix
        for ind, i in enumerate(f.readlines()):
            for indj, j in enumerate(map(int, i.strip().split(" "))):
                M[ind][indj] = j

        solver.M = M
        
        solver.row=solver.col = _n

    except Exception as e:
        print '\n Exception occured: %s Check again' % (e)
    finally:
        return solver


def fillFromBash():
    global _n,_MTX
    """Creates Hungarian instance problem using GUI filled matrix"""
    solver = HungarianAssignment()
    
    solver.M = _MTX
    
    '''solver.M = [[-1 for a in xrange(_n)]
                for b in xrange(_n)]  # denotes the matrix
    
    for i in xrange(_n):
        for j in xrange(_n):
            try:
                solver.M[i][j] = _MTX[i][j]
            except IndexError:
                solver.M[i][j] = 0'''

    solver.row = solver.col = _n
    return solver


#ToRunLinuxCommands
def run_cmd(args_list):
    """
    To Run Linux Commands
    """
    print 'Running system command: {0}'.format(' '.join(args_list))
    proc = subprocess.Popen(args_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (s_output, s_err) = proc.communicate()
    s_return = proc.returncode
    return s_output, s_err 


def main(fileHandle=None):
    global _backup, finalResult, backup_dc_id, _fileLocation, _fileName
    # Obtain matrix from file
    # or use matrix already filled by the GUI
    
    takingFileInput()
    
    takingNetworkInput()
    solver = fillFromBash() if _MTX else readInput()

    if solver.M is None:
        print ' Error occured during execution\n'
        exit()
    _backup = solver.M[:]
    print '\n Received Matrix: \n',
    solver.printMatrix()

    # Reduce the matrix
    solver.reduceMatrix()
    print '\n Reduced Matrix: \n',
    solver.printMatrix()

    # Get zero positions from the array
    solver.getZeroPositions()
    solver.printZeroLocations()

    # Check assignments
    solver.checkAssignments()
    #finalResult = solver.finalResult
    print color.BOLD +"The BackUp DC for the "+full_dc_id+" is "+str(backup_dc_id)+color.END,'\n\n'
    print '\t\t',
    (out,err)=run_cmd(['hadoop', 'distcp', 'hdfs://dc'+dc_id+':9000/myFiles/'+str(_fileName), 'hdfs://dc'+str(backup_dc_id)+':9000/backupFiles/'])
    print(err)
    print(out)

if __name__ == '__main__':
    main()
