On 20190719, I finally set out to code a Kakuro solver.

By the next morning, I was thinking about the most efficient way to solve it! I was surprised how simple the puzzle was to solve compared to the variety of deduction I have to go through to solve it manually.

It's possible the solver doesn't solve every puzzle, and that'd be a feature I'd like to add down the road: taking a picture of a puzzle and parsing it into text.

As for now, I'd like to pivot the code I have and see if it is easily modded into a Sudoku solver.

Remark: I also realize that the solver may currently contain excess code. As I'm currently satisfied with the solver's ability to solve some puzzles, I do not care to go through the mental exercise of removing excessive code.

On 20190720, I finished the Sudoku solver. Similar comments to the above. One extra comment is I've tried to tackle a Sudoku solver on one or two previous occasions and it felt cumbersome. In particular, the methods I attempted to implement were very closely tied to how I would solve a Sudoku puzzle manually. With that being said, I'm guessing I didn't implement classes to handle the different parts of the code and so the code likely became unmanageable.

Again, I'm first surprised that I ended up writing a computer-specific solution to Kakuro puzzles and that I was able to adapt it to a computer-specific solution to Sudoku puzzles. While the solutions border on being brute force, they are not completely brute force. However, part of the Kakuro solution runs so many possibilities that when applied to the Sudoku puzzle takes an incredibly long time without the proper set-up.