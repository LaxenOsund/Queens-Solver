test_board = [
    [0,0,1,1,1,2,2,2],
    [0,3,1,3,1,4,2,2],
    [0,3,1,3,1,2,2,2],
    [0,3,3,3,1,5,6,2],
    [0,3,3,3,1,5,6,6],
    [0,3,7,3,1,5,6,6],
    [7,3,7,3,1,5,5,6],
    [7,7,7,7,6,6,6,6]]
def solve(board):
    n = len(board)

    def touching(r1,c1,r2,c2):
        return abs(r1-r2)<= 1 and abs(c1-c2) <= 1
    def is_safe(r,c, queens, used_cols, used_regions):
        #en per c (Kolumn)
        if c in used_cols:
            return False

        region_id = board[r][c]
        if region_id in used_regions:
            return False
        
        for rr, cc in queens:
            if touching(rr, cc, r, c):
                return False
        return True
    
    queens = []
    used_cols = set()
    used_regions = set()

    def dfs(r):
        if r == n:
            return True
        for c in range(n):
            if is_safe(r, c, queens, used_cols, used_regions):
                queens.append((r, c))
                used_cols.add(c)
                used_regions.add(board[r][c])

                if dfs(r + 1):
                    return True

                queens.pop()
                used_cols.remove(c)
                used_regions.remove(board[r][c])
        return False

    ok = dfs(0)
    return queens if ok else None


def showsolve(board):
    ans = solve(board)
    n = len(board)
    for r in range(n):
        print(' '.join('♛' if (r, c) in ans else '·' for c in range(n)))
