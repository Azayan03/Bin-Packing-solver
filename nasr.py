import customtkinter as tk
from CTkMessagebox import CTkMessagebox
from genetic import *

from customtkinter import CTkCanvas


def ensure_closing():
    # get yes/no answers
    msg = CTkMessagebox(title="Exit?", message="Do you want to close the program?",
                        icon="question", option_1="Cancel", option_2="No", option_3="Yes")
    response = msg.get()

    if response == "Yes":
        root.destroy()
    else:
        print("Click 'Yes' to exit!")


def process_inputs(item_sizes, items_number, bin_capacity, num_bins):
    if len(item_sizes) < items_number:
        CTkMessagebox(title="Error", message=f"items number is {items_number} while there are {len(item_sizes)} items",
                      icon="cancel")
        return False

    elif len(item_sizes) > items_number:
        CTkMessagebox(title="Error",
                      message=f"Number of items is {items_number} while there are {len(item_sizes)} items",
                      icon="cancel")
        return False
    for item in item_sizes:
        if item > bin_capacity:
            CTkMessagebox(title="Error", message=f"Invalid input: there is an item bigger than Bin Capacity",
                          icon="cancel")
            return False

    if sum(item_sizes) > num_bins * bin_capacity:
        CTkMessagebox(title="Error", message=f"Invalid input: wrong number of bins",
                      icon="cancel")
        return False
    return True


class BinPackingSolverGUI:
    def __init__(self, root):
        tk.set_appearance_mode("Dark")
        tk.set_default_color_theme("blue")
        self.bin_capacity_var_entry = None
        self.item_sizes_var_entry = None
        self.num_bins_var_entry = None
        self.root = root
        self.root.title("Bin Packing-AI")
        self.average = 0
        self.canvas = tk.CTkCanvas(self.root, bg="#242424", bd=0, highlightthickness=0, relief='ridge')

        self.canvas.grid(row=6, column=0, columnspan=2, pady=10, sticky="nsew")
        self.colors = [
            '#E3D1E9', '#D9E8FB', '#D5E8D4', '#FEE3C7',
            '#FEEFCE', '#F5CDCA', '#B9C6D0', '#f032e6',
            '#bcf60c', '#fabebe', '#008080', '#e6beff',
            '#9a6324', '#fffac8', '#800000', '#aaffc3',
            '#808000', '#ffd8b1', '#808080',
        ]
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(6, weight=1)
        self.full_boxes_best_solution = 0
        self.current_animation_step = 0
        self.num_items_var_entry = None
        self.bin_capacity_var = None
        self.solution_found = False
        self.item_sizes_var = None
        self.num_items_var = None
        self.best_solution = None
        self.reached_heights = []
        self.animation_speed = 1
        self.num_bins_var = None
        self.boxes = []
        self.item_spacing = 1
        self.genetic_best_individual = []
        self.create_gui()

    def solve_backtracking(self, index, current_solution):
        if index == len(self.item_sizes_var):
            if self.is_better_solution(current_solution):
                self.best_solution = current_solution.copy()
                self.solution_found = True
            return

        for bin_index in range(self.num_bins_var):
            if self.can_add_to_bin(self.boxes[bin_index], self.item_sizes_var[index][0]):
                self.boxes[bin_index] += self.item_sizes_var[index][0]
                current_solution.append((self.item_sizes_var[index], bin_index))
                self.update_gui(current_solution, "backtrack")
                self.root.update()
                self.root.after(self.animation_speed)
                self.solve_backtracking(index + 1, current_solution)
                current_solution.pop()
                self.boxes[bin_index] -= self.item_sizes_var[index][0]
                self.update_gui(current_solution, "backtrack")
                self.root.update()
                self.root.after(self.animation_speed)
        self.update_gui(self.best_solution, "backtrack")
        self.draw_pipe_contentBest()

    def can_add_to_bin(self, bin_height, item_length):
        return item_length + bin_height <= self.bin_capacity_var

    def calculate_reached_height(self, current_solution):
        self.reached_heights = []
        for _ in range(self.num_bins_var + 1):
            self.reached_heights.append([])
        for i in current_solution:
            self.reached_heights[i[1]].append(i[0])

    def is_better_solution(self, new_solution):
        new_solution_full = set()
        for i in new_solution:
            new_solution_full.add(i[1])

        if self.best_solution is None:
            self.full_boxes_best_solution = len(new_solution_full)
            self.best_solution = new_solution
            return True

        if len(new_solution_full) < self.full_boxes_best_solution:
            self.full_boxes_best_solution = len(new_solution_full)
            self.best_solution = new_solution
            return True
        else:
            return False

    def update_gui(self, current_solution, algorithm_type, y_offset=0):
        self.canvas.delete("all")
        self.draw_boxes()

        if algorithm_type == "backtrack":
            for i in current_solution:
                self.draw_pipe(i[1] + 1, current_solution) #[((1,red),0) , ((4,blue),1) , ((2,green),0)]
        else:
            self.draw_pipe_genetic(current_solution)

        if current_solution:
            pipes_content = {i + 1: [] for i in range(len(self.boxes))}
            for i, (item_length, bin_index) in enumerate(current_solution):
                pipes_content[bin_index + 1].append(item_length[0])

            for pipe, content in pipes_content.items():
                content_str = " , ".join(map(str, content))
                self.draw_pipe_content(pipe, content_str, y_offset=y_offset)

    def draw_pipe(self, pipe_index, current_solution):
        self.calculate_reached_height(current_solution)
        items = self.reached_heights[pipe_index - 1]
        heightOfPrevItems = 0
        for i in range(len(items)):
            item_height = ceil(items[i][0] * (((self.canvas.winfo_height()) / self.bin_capacity_var) / 2.0))
            y = self.canvas.winfo_height()

            pipe_width = (((self.canvas.winfo_width()) / self.num_bins_var))
            pipe_width = (((self.canvas.winfo_width() - pipe_width) / self.num_bins_var))
            total_width = (((self.canvas.winfo_width() - pipe_width) - (pipe_width * self.num_bins_var)) / (
                    self.num_bins_var - 1))
            x = ((pipe_index * pipe_width))
            self.canvas.create_rectangle((x + total_width) - pipe_width / 2, y - (item_height + heightOfPrevItems),
                                         x + pipe_width / 2, y - heightOfPrevItems,
                                         fill=items[i][1])

            self.canvas.create_text(x + (total_width / 2), y - heightOfPrevItems - ceil(item_height / 2.0),
                                    text=str(items[i][0]), font=("Helvetica", 14), fill="black")
            heightOfPrevItems += item_height

    def draw_pipe_content(self, pipe_index, content, y_offset=0):
        x = 150
        y = 300 + y_offset
        self.canvas.create_text(x, y - (20 * pipe_index), text=f"pipe {pipe_index} : [ {content} ]",
                                font=("Helvetica", 14), fill="white")

    def draw_pipe_contentBest(self):
        if self.solution_found:
            self.canvas.create_text(500, 110, text="BEST SOLUTION FOUND!", font=("Helvetica", 22), fill="green")
            self.canvas.create_text(500, 150, text=f"minimum number of bins : {check_bins_number(self.best_solution)}",
                                    font=("Helvetica", 18),
                                    fill="green")

            best_solution_content = {i + 1: [] for i in range(len(self.boxes))}
            for i, (item_length, bin_index) in enumerate(self.best_solution):
                best_solution_content[bin_index + 1].append(item_length[0])

            for pipe, content in best_solution_content.items():
                content_str = " , ".join(map(str, content))
                x = 850
                y = 300
                self.canvas.create_text(x, y - (20 * pipe), text=f"pipe {pipe} : [ {content_str} ]",
                                        font=("Helvetica", 14), fill="green")

    def create_gui(self):
        tk.CTkLabel(self.root, text="Number of Items:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.num_items_var_entry = tk.CTkEntry(self.root)
        self.num_items_var_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        tk.CTkLabel(self.root, text="Number of Bins:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.num_bins_var_entry = tk.CTkEntry(self.root)
        self.num_bins_var_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        tk.CTkLabel(self.root, text="Item Sizes (comma-separated):").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.item_sizes_var_entry = tk.CTkEntry(self.root)
        self.item_sizes_var_entry.grid(row=2, column=1, padx=5, pady=5, sticky="ew")

        tk.CTkLabel(self.root, text="Bin Capacity:").grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.bin_capacity_var_entry = tk.CTkEntry(self.root)
        self.bin_capacity_var_entry.grid(row=3, column=1, padx=5, pady=5, sticky="ew")

        tk.CTkButton(self.root, text="Solve (Backtracking)", command=self.get_values).grid(row=4, column=0,
                                                                                           columnspan=2, pady=10,
                                                                                           sticky="ew")

        # Button to solve using Genetic Algorithm
        tk.CTkButton(self.root, text="Solve (Genetic Algorithm)", command=self.solve_genetic).grid(row=5, column=0,
                                                                                                   columnspan=2,
                                                                                                   pady=10,
                                                                                                   sticky="ew")

    def solve_genetic(self):

        self.num_items_var = int(self.num_items_var_entry.get())
        self.num_bins_var = int(self.num_bins_var_entry.get())
        self.bin_capacity_var = int(self.bin_capacity_var_entry.get())
        heightOfItemsFromUser = list(map(int, self.item_sizes_var_entry.get().split(',')))
        if process_inputs(heightOfItemsFromUser, self.num_items_var, self.bin_capacity_var, self.num_bins_var):
            self.item_sizes_var = []
            self.reached_heights = []
            self.boxes = [0] * self.num_bins_var

            item_sizes_pairs = [(size, i) for i, size in enumerate(heightOfItemsFromUser)]
            population_size = 1000
            num_generations = 1000
            best_individual = self.genetic_algorithm(population_size, num_generations, item_sizes_pairs,
                                                     heightOfItemsFromUser, self.num_bins_var,
                                                     self.bin_capacity_var)
            print(best_individual[1])

            self.update_gui(best_individual[1], "genetic")
            self.root.update()
            self.root.after(self.animation_speed - 90)
            self.draw_pipe_contentBest_genetic(best_individual[1], best_individual[0])

    def draw_pipe_contentBest_genetic(self, solution, min_bins):
        best_solution_content = {i + 1: [] for i in range(len(self.boxes))}
        for i, (item_length, bin_index) in enumerate(solution):
            best_solution_content[bin_index + 1].append(item_length[0])

        for pipe, content in best_solution_content.items():
            content_str = " , ".join(map(str, content))
            x = 850
            y = 300
            self.canvas.create_text(x, y - (20 * pipe), text=f"pipe {pipe} : [ {content_str} ]",
                                    font=("Helvetica", 14), fill="green")
            self.canvas.create_text(500, 110, text="BEST SOLUTION FOUND!", font=("Helvetica", 22), fill="green")
            self.canvas.create_text(500, 150, text=f"minimum number of bins : {min_bins}", font=("Helvetica", 18),
                                    fill="green")

    def genetic_algorithm(self, population_size, num_generations, items_pairs, items, num_bins, bin_capacity):
        best = (10000000, [])
        my_map = {}
            #[((items size, input index),)]
        population = [(generate_random_individual(items_pairs, num_bins, bin_capacity), 0) for _ in
                      range(population_size)]

        for generation in range(num_generations):  # 1 - 1000
            for i in range(len(population)):       #1 - 100
                individual, _ = population[i]
                fitness = evaluate_fitness(individual, items, num_bins, bin_capacity)
                population[i] = (individual, fitness)
                if fitness in my_map:
                    my_map[fitness] += 1
                else:
                    my_map[fitness] = 1

            best_individual, best_fitness = min(population, key=lambda x: x[1])
            #print(f"Generation {generation + 1}, Best Fitness: {best_fitness}, BestIndividual : {best_individual}")
            if not best_fitness >= 1000:
                self.update_gui(best_individual, "genetic")
                self.root.update()
                self.root.after(self.animation_speed - 90)
            if best[0] > best_fitness:
                best = (best_fitness, best_individual)

            parents = random.sample(population, k=population_size // 2)
            new_population = []

            for i in range(0, len(parents), 2):
                child1, child2 = crossover(parents[i][0], parents[i + 1][0], num_bins, bin_capacity)
                if i % 2 == 0:
                # Mutate the new individuals if needed
                    child1 = mutate(child1, num_bins, bin_capacity)
                    child2 = mutate(child2, num_bins, bin_capacity)

                new_population.extend([(child1, 0), (child2, 0)])

            population = new_population

        best_solution, _ = min(population, key=lambda x: x[1])
        sum = 0
        for i in my_map:
            sum += my_map[i]

        print(sum)
        print(my_map,"ccccccc")
        self.average += my_map[12]
        print(self.average)
        return best

    def draw_pipe_genetic(self, current_solution):
        self.calculate_reached_height(current_solution)
        # print(self.reached_heights,"ggggggggggggggggggggggggggg")
        items = self.reached_heights
        #print(items, "items")
        #print(current_solution)
        for i in range(len(items)):
            heightOfPrevItems = 0
            for reached in items[i]:
                item_height = ceil(reached[0] * (((self.canvas.winfo_height()) / self.bin_capacity_var) / 2.0))
                # print("items of", i, items[i], "and pipe index is ", pipe_index)
                y = self.canvas.winfo_height()

                pipe_width = (((self.canvas.winfo_width()) / self.num_bins_var))
                pipe_width = (((self.canvas.winfo_width() - pipe_width) / self.num_bins_var))
                total_width = (((self.canvas.winfo_width() - pipe_width) - (pipe_width * self.num_bins_var)) / (
                        self.num_bins_var - 1))
                x = (((i + 1) * pipe_width))
                # if isinstance(items[i][1], int):
                #   items[i][1] = "red"
                if reached[1] < 18:
                    fill_color = self.colors[reached[1]]
                else:
                    fill_color = self.random_hex_color()

                self.canvas.create_rectangle((x + total_width) - pipe_width / 2, y - (item_height + heightOfPrevItems),
                                             x + pipe_width / 2, y - heightOfPrevItems,
                                             fill=fill_color)

                self.canvas.create_text(x + (total_width / 2), y - heightOfPrevItems - ceil(item_height / 2.0),
                                        text=str(reached[0]), font=("Helvetica", 14), fill="black")
                heightOfPrevItems += item_height

    def draw_boxes(self):
        for i in range(self.num_bins_var):
            item_height = ceil(self.bin_capacity_var * (((self.canvas.winfo_height()) / self.bin_capacity_var) / 2.0))
            y = self.canvas.winfo_height()
            pipe_width = (((self.canvas.winfo_width()) / self.num_bins_var))
            pipe_width = (((self.canvas.winfo_width() - pipe_width) / self.num_bins_var))
            total_width = (((self.canvas.winfo_width() - pipe_width) - (pipe_width * self.num_bins_var)) / (
                    self.num_bins_var - 1))
            x = (((i + 1) * pipe_width))
            self.canvas.create_rectangle((x + total_width) - pipe_width / 2, y - item_height,  #(X1,Y1,X2,Y2)
                                         x + pipe_width / 2, y,
                                         fill="white", outline="black")

    def random_hex_color(self):
        # Generate random RGB values
        red = random.randint(0, 255)
        green = random.randint(0, 255)
        blue = random.randint(0, 255)

        # Format RGB values as a hexadecimal string
        hex_color = "#{:02X}{:02X}{:02X}".format(red, green, blue)

        return hex_color

    def get_values(self):
        self.num_items_var = int(self.num_items_var_entry.get())
        self.num_bins_var = int(self.num_bins_var_entry.get())
        self.bin_capacity_var = int(self.bin_capacity_var_entry.get())
        self.item_sizes_var = []
        heightOfItemsFromUser = list(map(int, self.item_sizes_var_entry.get().split(',')))
        if process_inputs(heightOfItemsFromUser, self.num_items_var, self.bin_capacity_var, self.num_bins_var):
            x = 0
            for i in heightOfItemsFromUser:

                if x > 18:
                    self.item_sizes_var.append((i, self.random_hex_color()))
                else:
                    self.item_sizes_var.append((i, self.colors[x]))
                x += 1
            self.boxes = [0] * self.num_bins_var
            self.reached_heights = []
            for _ in range(self.num_bins_var + 1):
                self.reached_heights.append([])
            self.best_solution = None
            self.solution_found = False
            self.full_boxes_best_solution = 0
            self.current_animation_step = 0
            self.item_spacing = 1
            self.solve_backtracking(0, [])


if __name__ == "__main__":
    root = tk.CTk()
    app = BinPackingSolverGUI(root)

    root.protocol("WM_DELETE_WINDOW", ensure_closing)

    window_width = 800
    window_height = 800

    # Get the screen width and height
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    # Calculate the x and y coordinates for the window to be centered
    x_position = (screen_width - window_width) // 2
    y_position = (screen_height - window_height) // 2
    root.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")

    root.mainloop()

