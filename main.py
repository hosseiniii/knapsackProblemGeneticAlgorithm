import random
import timeit
from typing import List
import numpy.random as npr

from answer import Answer
from individual import Individual


def read_individuals_from_file(file_name: str):
    with open(file_name, 'r') as f:
        file_matrix = [[int(num) for num in line.split(' ')] for line in f if line.strip() != ""]

    file_individuals: List[Individual] = []

    for individual in file_matrix:
        file_individuals.append(Individual(individual[0], individual[1]))

    return file_individuals


def read_config_file(file_name: str):
    with open(file_name, 'r') as f:
        file_data = [line.split(" ") for line in f]

    return int(file_data[0][2]), int(file_data[1][2]), float(file_data[2][2])


def make_initial_population(count: int, individuals: List[Individual], capacity: int) -> List[Answer]:
    initial_answers: List[Answer] = []

    for _ in range(count):
        temp_chromosome = [random.randint(0, 1) for _ in range(len(individuals))]

        total_value, total_weight = calculate_answer_weight_value(individuals, temp_chromosome)

        if total_weight <= capacity:
            initial_answers.append(Answer(temp_chromosome, total_weight, total_value))

    return initial_answers


def calculate_answer_weight_value(individuals, chromosome):
    total_weight = 0
    total_value = 0
    for index, item in enumerate(chromosome):
        if item == 1:
            total_weight += individuals[index].weight
            total_value += individuals[index].value
    return total_value, total_weight


def roulette_wheel(roulette_wheel_answers: List[Answer], count: int) -> List[Answer]:
    maxim = sum([_.total_value for _ in roulette_wheel_answers])
    selection_chance = [_.total_value / maxim for _ in roulette_wheel_answers]
    selected_answers = \
        [roulette_wheel_answers[npr.choice(len(roulette_wheel_answers), p=selection_chance)] for _ in range(count)]
    return selected_answers


def mutation(chromosome):
    probability = random.uniform(0.0, 1.0)
    if probability >= 1 - mutation_probability:
        mutation_location = random.randint(0, len(chromosome) - 1)
        chromosome[mutation_location] = 1 - chromosome[mutation_location]
    return chromosome


def crossover(crossover_answers: List[Answer], count: int, individuals: List[Individual]) -> List[Answer]:
    selected_old_answers = roulette_wheel(crossover_answers, count)

    crossover_point1: int = int(len(crossover_answers[0].chromosome) / 3)
    crossover_point2: int = int(crossover_point1 * 2)

    new_answers: List[Answer] = []
    for index in range(0, len(selected_old_answers), 2):
        temp_chromosome1 = \
            selected_old_answers[index].chromosome[:crossover_point1] + \
            selected_old_answers[index + 1].chromosome[crossover_point1:crossover_point2] + \
            selected_old_answers[index].chromosome[crossover_point2:]

        temp_chromosome1 = mutation(temp_chromosome1)

        total_value, total_weight = calculate_answer_weight_value(individuals, temp_chromosome1)

        if total_weight <= knapsack_capacity:
            new_answers.append(Answer(temp_chromosome1, total_weight, total_value))

        temp_chromosome2 = \
            selected_old_answers[index + 1].chromosome[:crossover_point1] + \
            selected_old_answers[index].chromosome[crossover_point1:crossover_point2] + \
            selected_old_answers[index + 1].chromosome[crossover_point2:]

        temp_chromosome2 = mutation(temp_chromosome2)

        total_value, total_weight = calculate_answer_weight_value(individuals, temp_chromosome2)

        if total_weight <= knapsack_capacity:
            new_answers.append(Answer(temp_chromosome2, total_weight, total_value))

    selected_new_answers = roulette_wheel(selected_old_answers + new_answers, count)

    return selected_new_answers


if __name__ == '__main__':

    start = timeit.default_timer()

    individuals = read_individuals_from_file("value_weight.txt")
    knapsack_capacity, initial_population_count, mutation_probability = read_config_file("config.txt")
    answers: List[Answer] = make_initial_population(initial_population_count, individuals, knapsack_capacity)

    new_crossover_answers: List[Answer] = answers
    for i in range(1000):
        new_crossover_answers = crossover(new_crossover_answers, initial_population_count, individuals)

    stop = timeit.default_timer()

    print("All Individuals total Values:")
    all_total_values = [_.total_value for _ in new_crossover_answers]
    print(all_total_values)
    print("All Individuals total Weights:")
    print([_.total_weight for _ in new_crossover_answers])
    print()
    print("Best Individual Value:", max(all_total_values))
    print("Best Individual Chromosome:",
          new_crossover_answers[all_total_values.index(max(all_total_values))].chromosome)
    print()
    print("Time: ", stop-start)
