import heapq
from functools import lru_cache

def bidirectional_astar(matrix, start, goal, obstacle_distance_map):
    if start == goal:
        return [start]  # Trivial case where start is the goal

    movements = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]  # 8-connected grid

    # Initialize forward and backward search structures
    open_list_start = []
    open_list_goal = []
    heapq.heappush(open_list_start, (heuristic(start, goal, obstacle_distance_map), start))  # Push start node with its heuristic estimate for start
    heapq.heappush(open_list_goal, (heuristic(goal, start, obstacle_distance_map), goal))  # Push goal node with its heuristic estimate for goal

    parent_start = {start: None}
    parent_goal = {goal: None}
    g_cost_start = {start: 0}
    g_cost_goal = {goal: 0}
    closed_start = set()
    closed_goal = set()

    while open_list_start and open_list_goal:
        # Expand the start side
        _, current_start = heapq.heappop(open_list_start)
        closed_start.add(current_start)

        if current_start in closed_goal:
            return reconstruct_path_bidirectional(parent_start, parent_goal, current_start)

        for dx, dy in movements:
            neighbor_start = (current_start[0] + dx, current_start[1] + dy)

            if not (0 <= neighbor_start[0] < len(matrix[0]) and 0 <= neighbor_start[1] < len(matrix)):
                continue

            if matrix[neighbor_start[1]][neighbor_start[0]] not in (0, 2):
                continue

            tentative_g_cost_start = g_cost_start[current_start] + (1.0 if dx == 0 or dy == 0 else 1.4)

            if neighbor_start in closed_start:
                continue

            if neighbor_start not in g_cost_start or tentative_g_cost_start < g_cost_start[neighbor_start]:
                parent_start[neighbor_start] = current_start
                g_cost_start[neighbor_start] = tentative_g_cost_start
                f_cost_start = tentative_g_cost_start + heuristic(neighbor_start, goal, obstacle_distance_map)
                heapq.heappush(open_list_start, (f_cost_start, neighbor_start))

                # Early exit if path found
                if neighbor_start in closed_goal:
                    return reconstruct_path_bidirectional(parent_start, parent_goal, neighbor_start)

        # Expand the goal side
        _, current_goal = heapq.heappop(open_list_goal)
        closed_goal.add(current_goal)

        if current_goal in closed_start:
            return reconstruct_path_bidirectional(parent_start, parent_goal, current_goal)

        for dx, dy in movements:
            neighbor_goal = (current_goal[0] + dx, current_goal[1] + dy)

            if not (0 <= neighbor_goal[0] < len(matrix[0]) and 0 <= neighbor_goal[1] < len(matrix)):
                continue

            if matrix[neighbor_goal[1]][neighbor_goal[0]] not in (0, 2):
                continue

            tentative_g_cost_goal = g_cost_goal[current_goal] + (1.0 if dx == 0 or dy == 0 else 1.4)

            if neighbor_goal in closed_goal:
                continue

            if neighbor_goal not in g_cost_goal or tentative_g_cost_goal < g_cost_goal[neighbor_goal]:
                parent_goal[neighbor_goal] = current_goal
                g_cost_goal[neighbor_goal] = tentative_g_cost_goal
                f_cost_goal = tentative_g_cost_goal + heuristic(neighbor_goal, start, obstacle_distance_map)
                heapq.heappush(open_list_goal, (f_cost_goal, neighbor_goal))

                # Early exit if path found
                if neighbor_goal in closed_start:
                    return reconstruct_path_bidirectional(parent_start, parent_goal, neighbor_goal)

    return None  # No path found

def reconstruct_path_bidirectional(parent_start, parent_goal, meeting_node):
    # Reconstruct path by following parents from both directions
    path_start = []
    node = meeting_node
    while node in parent_start:
        path_start.append(node)
        node = parent_start[node]
    path_start.reverse()

    path_goal = []
    node = meeting_node
    while node in parent_goal:
        path_goal.append(node)
        node = parent_goal[node]

    # Exclude the meeting node itself from one of the paths to avoid duplication
    return path_start[:-1] + path_goal if path_start[-1] == meeting_node else path_goal[:-1] + path_start

def heuristic(a, b, obstacle_distance_map):
    base_cost = abs(a[0] - b[0]) + abs(a[1] - b[1])
    penalty = 150 / (obstacle_distance_map[a[1]][a[0]] + 1)  # Adjust weight, using [][]
    return base_cost + penalty
