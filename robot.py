import random
import math
import hashlib
import struct


BASE62_ALPHABET = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"


def base62_encode(data: bytes) -> str:
    num = int.from_bytes(data, "big")
    if num == 0:
        return BASE62_ALPHABET[0]
    result = []
    while num > 0:
        num, rem = divmod(num, 62)
        result.append(BASE62_ALPHABET[rem])
    return ''.join(reversed(result))


def base62_decode(encoded: str) -> bytes:
    num = 0
    for char in encoded:
        num = num * 62 + BASE62_ALPHABET.index(char)
    byte_length = (num.bit_length() + 7) // 8
    return num.to_bytes(byte_length, "big")


def compress_floats(float_list):
    quantized = [int((f + 1) * 32767.5) for f in float_list]
    byte_data = struct.pack('>' + 'H' * len(quantized), *quantized)
    encoded_data = base62_encode(byte_data)
    return encoded_data


def decompress_floats(encoded_data):
    byte_data = base62_decode(encoded_data)
    quantized = struct.unpack('>' + 'H' * (len(byte_data) // 2), byte_data)
    return [(q / 32767.5) - 1 for q in quantized]


def fingerprint(float_list):
    byte_data = struct.pack('>' + 'f' * len(float_list), *float_list)
    hash_obj = hashlib.sha256(byte_data)
    fingerprint = hash_obj.hexdigest()
    return fingerprint


def leaky_relu(x, alpha=0.01):
    return x if x > 0 else alpha * x


def softmax(values):
    exp_values = [math.exp(v) for v in values]
    sum_exp_values = sum(exp_values)
    probabilities = [v / sum_exp_values for v in exp_values]
    return probabilities


def argmax(values):
    max_index = 0
    max_value = values[0]
    for i in range(1, len(values)):
        if values[i] > max_value:
            max_value = values[i]
            max_index = i
    return max_index


class Linear:
    def __init__(self, input_size, output_size, activation):
        self.input_size = input_size
        self.output_size = output_size
        self.activation = activation
        self.weights = [[random.uniform(-1, 1) for _ in range(input_size)] for _ in range(output_size)]
        self.biases = [random.uniform(-1, 1) for _ in range(output_size)]

    def forward(self, inputs):
        return [
            self.activation(sum(w * inp for w, inp in zip(weights, inputs)) + bias)
            for weights, bias in zip(self.weights, self.biases)
        ]

    def get_parameters(self):
        return [w for row in self.weights for w in row] + self.biases

    def set_parameters(self, parameters):
        for i in range(self.output_size):
            for j in range(self.input_size):
                self.weights[i][j] = parameters[i * self.input_size + j]
        self.biases = parameters[self.input_size * self.output_size:]


class NeuralNetwork:
    def __init__(self, input_size, hidden_size, output_size):
        self.input_layer = Linear(input_size, hidden_size, activation=leaky_relu)
        self.hidden_layer = Linear(hidden_size, hidden_size, activation=leaky_relu)
        self.output_layer = Linear(hidden_size, output_size, activation=leaky_relu)

    def forward(self, inputs):
        return self.output_layer.forward(self.hidden_layer.forward(self.input_layer.forward(inputs)))

    def get_parameters(self):
        return self.input_layer.get_parameters() + self.hidden_layer.get_parameters() + self.output_layer.get_parameters()

    def set_parameters(self, parameters):
        input_length = len(self.input_layer.get_parameters())
        hidden_length = len(self.hidden_layer.get_parameters())
        self.input_layer.set_parameters(parameters[:input_length])
        self.hidden_layer.set_parameters(parameters[input_length:input_length + hidden_length])
        self.output_layer.set_parameters(parameters[input_length + hidden_length:])


shared_state = [0.0, 0.0, 0.0, 0.0, 0.0]
network = NeuralNetwork(input_size=12, hidden_size=24, output_size=12)
network.set_parameters(decompress_floats(
"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"
))


def health_by_coords(state, coord):
    obj = state.obj_by_coords(coord)
    if obj and obj.team is not None:
        return obj.health / 5 if obj.team == state.our_team else -obj.health / 5
    return 0


def robot(state, unit):
    global shared_state

    x = (float(unit.coords.x) - 10) / 10
    y = (float(unit.coords.y) - 10) / 10
    r = math.sqrt(x * x + y * y)
    inputs = [x, y, r] + [
        health_by_coords(state, coord) for coord in unit.coords.coords_around()
    ] + shared_state

    output = network.forward(inputs)
    action_value, direction_value, decay_coeff, shared_updates = output[:2], output[2:6], output[7], output[7:]

    total_units = len(state.ids_by_team(state.our_team)) + len(state.ids_by_team(state.other_team))
    memory_decay = (1 + math.tanh(decay_coeff)) * (1 + math.tanh(total_units - 20)) / 4
    shared_state[:] = [
        math.tanh((1 - memory_decay) * s + memory_decay * u)
        for s, u in zip(shared_state, shared_updates)
    ]

    action_type = [ActionType.Move, ActionType.Attack][argmax(softmax(action_value))]
    direction = [
        Direction.North,
        Direction.South,
        Direction.East,
        Direction.West
    ][argmax(softmax(direction_value))]

    return Action.move(direction) if action_type == ActionType.Move else Action.attack(direction)
