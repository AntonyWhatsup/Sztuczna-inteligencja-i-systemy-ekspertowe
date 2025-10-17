import random
from genome import random_genome, mutate
from evaluation import evaluate
from visualization import plot_pareto

def evolve(pop_size, generations, mutation_rate):
    # each individual = (genome, angles)
    population = [random_genome() for _ in range(pop_size)]
    results = []

    for gen in range(generations):
        # evaluate each individual
        scored = [(g, evaluate(g[0], g[1])) for g in population]

        # sort by energy descending, cost ascending
        scored.sort(key=lambda s: (-s[1][0], s[1][1]))

        # keep best half
        survivors = [g for g, _ in scored[:pop_size//2]]

        # reproduce with mutation
        children = [mutate(g[0], g[1]) for g in random.choices(survivors, k=pop_size//2)]

        # combine
        population = survivors + children

        results.extend(scored)
        print(f"Generation {gen+1}/{generations} done")

    plot_pareto(results)
    return results
