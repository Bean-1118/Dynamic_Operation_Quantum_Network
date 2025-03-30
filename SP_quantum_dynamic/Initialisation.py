import numpy as np
import networkx as nx
import math
import random

# Set seed for reproducibility
RANDOM_SEED = 42  # You can change this value if needed
random.seed(RANDOM_SEED)
np.random.seed(RANDOM_SEED)

# Constants for Dynamic Time Simulation
Q_LIMIT = 100  # Maximum number of queued events allowed
BUSY = 1  # Status indicator when the server is busy
IDLE = 0  # Status indicator when the server is idle

# Global variables for simulation
next_event_type = 0  # Determines the type of the next event (arrival or departure)
num_in_q = 0  # Number of customers currently in the queue
server_status = IDLE  # Tracks whether the server is busy or idle

# Statistical accumulators
area_num_in_q = 0.0  # Accumulates the area under the queue length curve
area_server_status = 0.0  # Accumulates the area under the server status curve
mean_interarrival = 0.0  # Mean interarrival time for new requests
mean_service = 0.0  # Mean service time for processing requests
sim_time = 0.0  # Tracks the current simulation time
time_arrival = [0.0] * (Q_LIMIT + 1)  # List storing arrival times of customers in queue
time_last_event = 0.0  # Stores the last event time in the simulation
time_next_event = [0.0] * 3  # Stores the times of the next events (arrival and departure)


def initialize():
    """Initialize simulation variables and reset statistics."""
    global sim_time, server_status, num_in_q, time_last_event
    global area_num_in_q, area_server_status, time_next_event

    sim_time = 0.0  # Reset simulation time
    server_status = IDLE  # Server starts as idle
    num_in_q = 0  # No customers in queue
    time_last_event = 0.0  # Last event time is set to zero

    # Reset statistical accumulators
    area_num_in_q = 0.0
    area_server_status = 0.0

    # Schedule first arrival event and set a high value for departure event
    time_next_event[1] = sim_time + expon(mean_interarrival)
    time_next_event[2] = 1.0e30  # Large value indicating no departure initially


def expon(mean):
    """Generate an exponentially distributed random variable."""
    return -mean * math.log(random.random())  # Uses the inverse transform method


def initialize_quantum_network(n, m, p=0.1, Qc=1):
    """
    Initialize a quantum network as a 2D grid graph with custom attributes.

    Parameters:
    n (int): Number of rows in the grid.
    m (int): Number of columns in the grid.
    p (float): Probability of entanglement between edges.
    Qc (int): Decoherence time affecting entanglement quality.

    Returns:
    nx.Graph: A NetworkX graph representing the quantum network.
    """
    G = nx.grid_2d_graph(n, m)  # Create a grid graph with n x m nodes
    nx.set_edge_attributes(G, 1, "length")  # Set default edge length to 1 km
    update_graph_params(G, p=p, Qc=Qc)  # Update graph parameters
    reset_graph_state(G)  # Reset entanglement status
    reset_graph_usage(G)  # Reset usage statistics
    return G


def reset_graph_state(G):
    """Reset entanglement and age attributes for nodes and edges."""
    nx.set_edge_attributes(G, False, "entangled")  # Mark all edges as not entangled
    nx.set_node_attributes(G, False, "entangled")  # Mark all nodes as not entangled
    nx.set_edge_attributes(G, 0, "age")  # Reset edge aging parameter
    nx.set_node_attributes(G, 0, "age")  # Reset node aging parameter


def reset_graph_usage(G):
    """Reset the usage counters for all nodes."""
    nx.set_node_attributes(G, 0, "usage_count")  # Set usage count to zero for all nodes
    nx.set_node_attributes(G, 0, "usage_fraction")  # Set usage fraction to zero for all nodes


def update_graph_params(G, p=None, Qc=None):
    """Update quantum network parameters such as decoherence time and entanglement probability."""
    if Qc is not None:
        nx.set_node_attributes(G, Qc, "Qc")  # Assign decoherence time to nodes
        nx.set_edge_attributes(G, Qc, "Qc")  # Assign decoherence time to edges
    if p is not None:
        nx.set_edge_attributes(G, p, "p_edge")  # Assign entanglement probability to edges


def initialize_dynamic_operation(mean_interarrival, mean_service):
    """
    Initialize parameters for the dynamic operation of the simulation.

    Parameters:
    mean_interarrival (float): Average time between arrivals.
    mean_service (float): Average service time.

    Returns:
    dict: Dictionary containing initialized dynamic operation parameters.
    """
    initialize()  # Reset simulation state
    return {
        "mean_interarrival": mean_interarrival,
        "mean_service": mean_service
    }


def initialize_simulation(quantum_grid_size, dynamic_params):
    """
    Initialize both the quantum network and dynamic operation.

    Parameters:
    quantum_grid_size (tuple): (rows, columns) defining the quantum network grid.
    dynamic_params (dict): Parameters for dynamic simulation.

    Returns:
    dict: Contains the initialized quantum network and dynamic operation parameters.
    """
    quantum_network = initialize_quantum_network(*quantum_grid_size)  # Create quantum network
    dynamic_operation = initialize_dynamic_operation(**dynamic_params)  # Initialize dynamic simulation
    return {
        "quantum_network": quantum_network,
        "dynamic_operation": dynamic_operation
    }


if __name__ == "__main__":
    # Example initialization parameters
    quantum_grid_size = (3, 3)  # Define a 3x3 quantum network grid
    dynamic_params = {
        "mean_interarrival": 5.0,  # Set mean interarrival time
        "mean_service": 3.0  # Set mean service time
    }

    # Run initialization process
    simulation_data = initialize_simulation(quantum_grid_size, dynamic_params)
    print("Quantum Network and Dynamic Operation Initialized Successfully.")
