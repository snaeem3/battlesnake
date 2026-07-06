from collections import deque

def floodFill(grid: list[list[bool]], i: int, j: int) -> int:
    if grid[i][j]:
        return 0

    rows, cols = len(grid), len(grid[0])

    queue = deque([(i, j)])
    grid[i][j] = True      # mark visited immediately
    count = 1

    while queue:
        i, j = queue.popleft()

        for di, dj in [(1,0), (-1,0), (0,1), (0,-1)]:
            ni, nj = i + di, j + dj

            if (0 <= ni < rows and
                0 <= nj < cols and
                not grid[ni][nj]):

                grid[ni][nj] = True
                queue.append((ni, nj))
                count += 1

    return count