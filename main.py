import pygame
import math

pygame.init()

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720

main_screen = pygame.display.set_mode(size=(SCREEN_WIDTH, SCREEN_HEIGHT))
main_screen.fill((255, 255, 255))

font = pygame.font.Font("cmunbi.ttf", 24)
num_font = pygame.font.Font("lmroman10-regular.otf", 18)

minimum_x = -9
maximum_x = 9

minimum_y = -7.5
maximum_y = 7.5

# the step size between each increment in x and y axes
step_x = 1
step_y = 1

# a horizontal offset applied to the plane to allow space for user input
offset = 300

# where all user controls lies
side_rect = pygame.Rect(0, 0, offset, SCREEN_HEIGHT)

# scaling factor for the x-axis
factor_x = abs((SCREEN_WIDTH - offset)/(maximum_x - minimum_x))

# scaling factor for the y-axis
factor_y = abs(SCREEN_HEIGHT/(maximum_y - minimum_y))

# shift in y-axis
y_axis_shift = (SCREEN_WIDTH - offset)/2 - factor_x*(minimum_x+maximum_x)/2 + offset

# shift in x-axis
x_axis_shift = SCREEN_HEIGHT/2 - factor_y*(minimum_y+maximum_y)/2


# returns a surface with an x and y axes on it
# **min max and customizable scaling to be added later**
def axis():
    surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    surface.set_colorkey((0, 0, 0))
    # x axis
    pygame.draw.line(
        surface, color=(50, 50, 50),
        start_pos=(0, x_axis_shift),
        end_pos=(SCREEN_WIDTH, x_axis_shift)
    )

    # drawing the increments on the x-axis
    # where a difference of factor_x corresponds to a difference of 1 on the plane
    i = 1
    # left of y-axis
    while i*factor_x*step_x < y_axis_shift:
        pygame.draw.line(
            surface, color=(200, 200, 200),
            start_pos=(-i * factor_x*step_x + y_axis_shift, 0),
            end_pos=(-i * factor_x*step_x + y_axis_shift, SCREEN_HEIGHT),
        )
        surface.blit(
            num_font.render(str(round(-step_x*i, 2)), True, (8, 8, 8)),
            (-i * factor_x*step_x + y_axis_shift - 4, x_axis_shift)
        )
        i += 1

    i = 1
    # right of y-axis
    while i*factor_x*step_x < SCREEN_WIDTH - y_axis_shift:
        pygame.draw.line(
            surface, color=(200, 200, 200),
            start_pos=(i*factor_x*step_x+y_axis_shift, 0),
            end_pos=(i*factor_x*step_x+y_axis_shift, SCREEN_HEIGHT),
        )
        surface.blit(
            num_font.render(str(round(step_x*i, 2)), True, (8, 8, 8)),
            (i * factor_x*step_x + y_axis_shift - 4, x_axis_shift)
        )
        i += 1

    # y-axis
    pygame.draw.line(
        surface, color=(50, 50, 50),
        start_pos=(y_axis_shift, 0),
        end_pos=(y_axis_shift, SCREEN_HEIGHT)
        )
    # drawing the increments on the y-axis
    # where a difference of factor_y corresponds to a difference of 1 on the plane
    i = 1
    # below x-axis
    while i * factor_y*step_y < SCREEN_HEIGHT - x_axis_shift:

        pygame.draw.line(
            surface, color=(200, 200, 200),
            start_pos=(0, i * factor_y * step_y + x_axis_shift),
            end_pos=(SCREEN_WIDTH, i * factor_y * step_y + x_axis_shift),
        )
        surface.blit(
            num_font.render(str(round(-step_y*i, 2)), True, (8, 8, 8)),
            (y_axis_shift - 20, i * factor_y * step_y + x_axis_shift - 14)
        )
        i += 1

    # above x-axis
    i = 1
    while i * factor_y*step_y < x_axis_shift:

        pygame.draw.line(
            surface, color=(200, 200, 200),
            start_pos=(0, -i * factor_y * step_y + x_axis_shift),
            end_pos=(SCREEN_WIDTH, -i * factor_y * step_y + x_axis_shift),
        )
        surface.blit(
            num_font.render(str(round(step_y*i, 2)), True, (8, 8, 8)),
            (y_axis_shift - 15, -i * factor_y * step_y + x_axis_shift - 14)
        )
        i += 1

    return surface


# this class handles most things related to the graphing functions
class Graph:
    def __init__(self, attached_text):
        self.function = lambda x: eval("")
        self.graph_coords = self.get_coords()
        self.graph_surf = self.plot()
        self.attached_text = attached_text

    # returns an array of tuples representing a set of coordinates that satisfy the graph
    def get_coords(self):
        coords = []
        n = minimum_x
        while n < maximum_x:
            # the try and except is to avoid the program crashing when a value is outside the real domain of a function
            try:
                coords.append((n, self.function(n)))
            except (SyntaxError, NameError, ValueError):
                pass

            # the accuracy increases as we lessen the interval
            # which is the same as zooming in
            n += factor_x / 10000

        return coords

    # returns a surface with plotted coordinates of passed graph (making use of local linearity)
    # still has bugs for functions like x^x
    def plot(self):
        surface = pygame.Surface(size=(SCREEN_WIDTH, SCREEN_HEIGHT))
        surface.set_colorkey((0, 0, 0))
        for i in range(1, len(self.graph_coords)):
            # a fix to drawing long lines across vertical asymptotes
            if abs(self.graph_coords[i - 1][1] - self.graph_coords[i][1]) > 60:
                continue
            pygame.draw.line(
                surface,
                color=(1, 1, 1),
                start_pos=(
                    factor_x * self.graph_coords[i - 1][0] + y_axis_shift,
                    -factor_y * self.graph_coords[i - 1][1] + x_axis_shift
                ),
                end_pos=(
                    factor_x * self.graph_coords[i][0] + y_axis_shift,
                    -factor_y * self.graph_coords[i][1] + x_axis_shift
                ),
                width=2
            )
        return surface

    def update_graph(self):
        def function(x):
            return eval(self.attached_text.text)

        self.function = lambda x: function(x)
        self.graph_coords = self.get_coords()
        self.graph_surf = self.plot()

    def draw_graph(self):
        main_screen.blit(self.graph_surf, (0, 0))


# this class handles everything related to the textbox
class TextBox:
    box_color_clicked = (255, 255, 255)
    box_color_not_clicked = (155, 155, 155)

    def __init__(self, position, size):
        self.position = position
        self.size = size
        self.body = pygame.Rect(position, size)
        self.text = ""
        self.clicked = False
        self.box_color = TextBox.box_color_not_clicked
        self.text_surface = font.render(self.text, True, (1, 1, 1))

        # label information
        self.label = font.render("", True, (1, 1, 1))
        self.label_text = ""
        self.label_position = position

    def process_events(self):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.body.collidepoint(event.pos):
                self.clicked = True
                self.box_color = TextBox.box_color_clicked
            else:
                self.clicked = False
                self.box_color = TextBox.box_color_not_clicked
        if event.type == pygame.KEYDOWN:
            if self.clicked:
                if event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                elif event.key == pygame.K_RETURN:
                    return
                else:
                    self.text += event.unicode
            # updating the text_surface for every change in the text
            self.text_surface = font.render(self.text, True, (1, 1, 1))

    def give_label(self, label_text):
        self.label_text = label_text
        width = self.size[0]
        x, y = self.position
        self.label_position = (x + width / 2 - len(self.label_text) * 6.2, y - 32)
        self.label = font.render(label_text, True, (1, 1, 1))

    # handles drawing the text_box and the text_surface (to be called every loop)
    def draw_text_box(self):
        pygame.draw.rect(main_screen, self.box_color, self.body)
        main_screen.blit(self.text_surface, self.position)
        if self.label_text != "":
            main_screen.blit(self.label, self.label_position)


# updates necessary values to match new domain
def update_values():
    global minimum_x
    global maximum_x
    global factor_x
    global factor_y
    global y_axis_shift
    global x_axis_shift
    global step_x
    global step_y
    global minimum_y
    global maximum_y

    # updating the min and max for x-axis
    try:
        temp = eval(domain_min.text)
        if temp < maximum_x:
            minimum_x = temp
    except (SyntaxError, NameError):
        pass
    try:
        temp = eval(domain_max.text)
        if temp > minimum_x:
            maximum_x = temp
    except (SyntaxError, NameError):
        pass

    # updating the min and max for the y-axis
    try:
        temp = eval(range_min.text)
        if temp < maximum_y:
            minimum_y = temp
    except (SyntaxError, NameError):
        pass
    try:
        temp = eval(range_max.text)
        if temp > minimum_y:
            maximum_y = temp
    except (SyntaxError, NameError):
        pass

    # updating the step value for the x and y axes
    try:
        step_x = eval(step_size_x.text)
    except (SyntaxError, NameError):
        pass

    try:
        step_y = eval(step_size_y.text)
    except (SyntaxError, NameError):
        pass

    factor_x = abs((SCREEN_WIDTH - offset) / (maximum_x - minimum_x))
    y_axis_shift = (SCREEN_WIDTH - offset) / 2 - factor_x * (minimum_x + maximum_x) / 2 + offset

    factor_y = abs(SCREEN_HEIGHT / (maximum_y - minimum_y))
    x_axis_shift = SCREEN_HEIGHT / 2 + factor_y * (minimum_y + maximum_y) / 2


def handle_drawing():
    main_screen.fill((255, 255, 255))
    main_screen.blit(current_axis, (0, 0))
    for function in functions:
        function.draw_graph()
    pygame.draw.rect(main_screen, (230, 230, 230), side_rect)
    for box in text_boxes:
        box.draw_text_box()
    pygame.display.flip()


function_input = TextBox((10, 100), (280, 50))
function_input.give_label("functions")
function_input2 = TextBox((10, 155), (280, 50))
function_input3 = TextBox((10, 210), (280, 50))

domain_min = TextBox((16, 400), (130, 50))
domain_min.give_label("x min")
domain_max = TextBox((156, 400), (130, 50))
domain_max.give_label("x max")

range_min = TextBox((16, 600), (130, 50))
range_min.give_label("y min")
range_max = TextBox((156, 600), (130, 50))
range_max.give_label("y max")

step_size_x = TextBox((80, 310), (130, 50))
step_size_x.give_label("x step size")
step_size_y = TextBox((80, 510), (130, 50))
step_size_y.give_label("y step size")

text_boxes = [function_input, function_input2, function_input3,
              domain_min, domain_max, step_size_x,
              range_min, range_max, step_size_y]

input_graph = Graph(function_input)
input_graph2 = Graph(function_input2)
input_graph3 = Graph(function_input3)
functions = [input_graph, input_graph2, input_graph3]

current_axis = axis()


# main loop
clock = pygame.time.Clock()
running = True
while running:
    clock.tick(30)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            break

        for text_box in text_boxes:
            text_box.process_events()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                # once the user presses enter, the input text is turned into a function that is then graphed
                update_values()
                for graph in functions:
                    graph.update_graph()
                current_axis = axis()
                break

    # copying/drawing all the contents into the main screen, which is what is displayed
    handle_drawing()

pygame.quit()
