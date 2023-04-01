import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import random
import copy
matplotlib.use('agg')


def f(x, delta_big):
    return np.array([1, x[0]**2, x[1]**2,
                     mu1(x[0], delta_big), mu1(x[0], delta_big) * x[0]**2, mu1(x[0], delta_big) * x[1]**2,
                     mu2(x[1], delta_big), mu2(x[1], delta_big) * x[0]**2, mu2(x[1], delta_big) * x[1]**2])


def mu1(x, delta_big):
    if x <= -delta_big:
        return 1
    elif -delta_big < x <= delta_big:
        return (delta_big - x) / (2 * delta_big)
    else:
        return 0


def mu2(x, delta_big):
    return 1 - mu1(x, delta_big)


def create_plan(grid, N):
    x = [(random.choice(grid), random.choice(grid)) for _ in range(N)]
    p = [1.0 / N for _ in range(N)]
    return x, p


def create_grid(gridN):
    print('create grid')
    n = gridN / 2
    return np.arange(-1, 1 + 0.5 / n, 1.0 / n)


def create_grid2D(grid, plan):
    grid2D = [(_x, _y) for _x in grid for _y in grid]
    # return [item for item in grid2D if item not in plan[0]]
    return grid2D  # Если повторные наблюдения разрешены


def find_m(x, p, delta_big):
    n = len(f((0, 0), delta_big))
    M = np.zeros((n, n))
    for i in range(len(x)):
        fx = f(x[i], delta_big)
        M += p[i] * np.outer(fx, fx.T)
    return M


def d(x_, xj, D, delta_big):
    return np.dot(np.dot(f(x_, delta_big).T, D), f(xj, delta_big))


def calc_delta(x, xj, D, N, delta_big):
    return 1.0 / N * (d(x, x, D, delta_big) - d(xj, xj, D, delta_big)) - \
           1.0 / N**2 * (d(x, x, D, delta_big) * d(xj, xj, D, delta_big) - d(x, xj, D, delta_big)**2)


def save_plan_plot(plan, gridN, N, info):
    x = plan[0]
    title = f'plot {gridN}-{N} ({info}).png'
    plt.clf()
    plt.title(title)
    for i in range(len(x)):
        plt.scatter(x[i][0], x[i][1])
    plt.savefig(f'{title}')
    return title


def alg_fedorova(gridN=20, N=20, delta_big=0.5):
    grid = create_grid(gridN)
    plan = create_plan(grid, N)
    plan0 = copy.deepcopy(plan)
    eps = 1e-3
    iteration = 0
    while True:
        yield f'Iteration {iteration:3d}.  '
        grid2D = create_grid2D(grid, plan)
        M = find_m(plan[0], plan[1], delta_big)
        D = np.linalg.inv(M)
        x_s = grid2D[0]
        delta_max = calc_delta(x_s, plan[0][0], D, N, delta_big)
        i_max = 0
        for i, xj in enumerate(plan[0]):
            for x in grid2D:
                delta = calc_delta(x, xj, D, N, delta_big)
                if delta > delta_max:
                    delta_max = delta
                    x_s = x
                    i_max = i
        yield f'delta_max = {delta_max:+.8e}   |M| = {np.linalg.det(M):.8e}\n'
        if delta_max < eps:
            yield f'{delta_max:+.8e} < {eps} (delta_max < eps)\n'
            break
        plan[0][i_max] = x_s
        iteration += 1
    yield plan0, plan, gridN
