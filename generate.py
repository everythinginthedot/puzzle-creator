import sys
import random
from crossword import *
from PIL import Image, ImageDraw, ImageFont
import copy


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def show_domains(self):
        return self.domains

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        _, _, w, h = draw.textbbox((0, 0), letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        for variable in self.domains:
            for word in self.domains[variable].copy():
                if len(word) != variable.length:
                    self.domains[variable].remove(word)

    

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        revision_made = False
        if self.crossword.overlaps[(x, y)] != None:
            overlap = self.crossword.overlaps[(x, y)]
            

            for word_x in self.domains[x].copy():
                if any(word_x[overlap[0]] == word_y[overlap[1]] for word_y in self.domains[y].copy()):
                    #print('norm slovo')
                    continue
                else:
                    revision_made = True
                    #print('slovo govno')
                    self.domains[x].remove(word_x)
            return revision_made
        
        else:
            return revision_made

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        if arcs == None:
            queue = list(self.crossword.overlaps.keys())
        else:
            queue = arcs

        i = 1
        while queue != []:

            arc = queue[0]
            '''
            print(f'Iteration: {i}')
            print(f'Current arc: {arc, self.crossword.overlaps[arc]}')
            print(f'Arcs in queue: {len(queue)}')
            print(f'Current queue: {queue}')
            i+=1
            '''
            queue.remove(arc)
            if self.revise(arc[0], arc[1]):
                #print('Revision')
                if self.domains[arc[0]] == {}:
                    return False
                neighbors = self.crossword.neighbors(arc[0])
                #print(f'neighbors: {neighbors}')
                neighbors.remove(arc[1])
                
                for neighbor in neighbors:
                    #print(f'Added neighbor: {neighbor}')
                    queue.append((neighbor, arc[0]))
            #print('\n')
        
        return True
        
        

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        #print('fisrt check')
        if len(assignment) == len(self.domains):
            #print('second check')
            for variable in assignment.keys():
                #print('assiment check')
                if assignment[variable] == None: # or len(assignment[variable]) != 1
                    print('assignment 1')
                    return False
            return True
        else:
            print('assignment 2')
            return False

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        i = 1
        #unassigned = self.domains.copy()
        #unassigned = {k: v for k, v in unassigned.items() if k not in assignment}
      
        for variable in assignment:
            for neighbor in self.crossword.neighbors(variable):
                if neighbor in assignment:
                    if assignment[variable] == assignment[neighbor]:
                        return False
                    else:
                        arc = self.crossword.overlaps[(variable, neighbor)]

                        if assignment[variable][arc[0]] == assignment[neighbor][arc[1]]:
                            continue
                        else:
                            return False
                            '''
                            print(f'Iteration: {i}')
                            i+=1
                            print(f'Variables: {variable, neighbor}')
                            print(f'Arc: {arc}')
                            print(f'Words: {word_variable, word_neighbor}')
                            print('\n')
                            '''                      
        return True
        

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        words_order = dict({word: 0 for word in self.domains[var]})
        for word_variable in words_order.keys():
            for neighbor in self.crossword.neighbors(var):
                if neighbor in assignment:
                    continue
                else:
                    arc = self.crossword.overlaps[(var, neighbor)]
                    for word_neighbor in self.domains[neighbor]:
                        if word_variable[arc[0]] != word_neighbor[arc[1]]:
                            words_order[word_variable] = words_order[word_variable] + 1

        #print(f'Words order values: {words_order}')
        
        inverted_words_order = {}
        sorted_keys = sorted(words_order, key=words_order.get)  

        for w in sorted_keys:
            inverted_words_order[w] = words_order[w]

        sorted(inverted_words_order)

        
        return list(inverted_words_order.keys())
                    
        

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """

        
        unassigned = {k: v for k, v in self.domains.copy().items() if k not in assignment}
        variable_order = dict({variable: len(unassigned[variable])for variable in unassigned})
        print(f'unassigned: {dict({variable: len(unassigned[variable]) for variable in unassigned})}')
        #{unassigned}
        print('\n')
        inverted_variable_order = {}
        for k, v in variable_order.items():
            inverted_variable_order[v] = inverted_variable_order.get(v, []) + [k]

        sorted_inverted_variable_order = dict(sorted(inverted_variable_order.items()))
        print(f'Sorted inverted variable order: {sorted_inverted_variable_order}')
        print('\n') 

        #sorting by degree
        if len(list(sorted_inverted_variable_order.values())[0]) > 1:
            variable_order_degree = dict({variable: len(self.crossword.neighbors(variable)) for variable in list(sorted_inverted_variable_order.values())[0]})
            print(f'Order of variables by Degree: {variable_order_degree}')
            print('\n')

            inverted_variable_order_degree = {}
            for k, v in variable_order_degree.items():
                inverted_variable_order_degree[v] = inverted_variable_order_degree.get(v, []) + [k]

            sorted_inverted_variable_order_degree = dict(sorted(inverted_variable_order_degree.items(), reverse=True))
            print(f'Sorted order of variables by degree: {sorted_inverted_variable_order_degree}')
            print('\n')

            if len(list(sorted_inverted_variable_order_degree.values())[0]) > 1:
                return random.choice(list(sorted_inverted_variable_order_degree.values())[0])
            else: return list(sorted_inverted_variable_order_degree.values())[0][0]

        else: return list(sorted_inverted_variable_order.values())[0][0]

    def check(self, variable):
        #overlaps = self.crossword.overlaps.keys()
        arcs = list(((x, y) for x, y in self.crossword.overlaps.keys() if x == variable and y in self.crossword.neighbors(variable)))
        return arcs


    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        print(f'Assignment backtrack: {assignment}')
        if self.assignment_complete(assignment):
            return assignment
        variable = self.select_unassigned_variable(assignment)
        pseudo_assigment = copy.deepcopy(assignment)
        pseudo_assigment.update({variable: self.domains[variable]})
        for word in self.order_domain_values(variable, assignment):
            
            pseudo_assigment.update({variable: word})
            if self.consistent(pseudo_assigment):
                
                assignment.update({variable: word})
                arcs = list(((x, y) for x, y in self.crossword.overlaps.keys() if x == variable and y in self.crossword.neighbors(variable)))
                self.ac3(arcs)
                result = self.backtrack(assignment)
                if result != False:
                    return result
                assignment.pop(variable)
        print('backtrack')
        return False


def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
