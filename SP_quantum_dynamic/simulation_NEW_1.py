import networkx as nx
import numpy as np
import random
from Dynamic_Time_Advanced import initialize, timing, arrive, depart, update_time_avg_stats, expon
import random
import Initialisation
from networkx.algorithms.approximation.steinertree import steiner_tree

# Set seed for reproducibility
RANDOM_SEED = 42  # You can change this value if needed
random.seed(RANDOM_SEED)
np.random.seed(RANDOM_SEED)

from graph import (
    reset_graph_usage,
    update_graph_usage,
    update_usage_from_subgraph,
    reset_graph_state,
    get_entangled_subgraph,
)
from sim import run_entanglement_step

def SP_protocol(G, users, timesteps, reps, count_fusion=False):
    """
    Shortest Path protocol taken from [SPsource] The protocol attempts to generate bell pairs between a central node and a set of users.
    This is done by attmepting entanglement along a set of edge disjoint paths, all connected to the centre node. The protocol
    requires a graph with only the edges required for SP routing are present. The protocol terminates once an entanglement is shared between
    the centre and all other users

    Input Pararmeters:
    G         - Networkx graph G(V,E) which defines the topology of the network. see graphs.py for more details
    users     - List of nodes in G which between which a GHZ should be shared. users[0] is the centre of the star which should be calculated before sending to SP_protocol
    timesteps - number of timesteps the protocol will run for before terminating without a successful GHZ generation,
    reps      - number of repetions the protocol will run for the imput parameters to generate a dataset.

    Outputs:
    rate                   -  entanglement rate (ER) (average GHZs generated per timeslot)
    multipartite_gen_time  -  array (length of reps)  array of timesteps until successful GHZ generated, if no successful GHZ generated value is -1
    avg_links_used         -  number of entanglement links used per repetition for successful GHZ generation
    """
    J = _get_star(
        G, users
    )  # get the shortest star in G, which connects all destination_nodes to the source_node

    er, multipartite_gen_time, avg_links_used = _run_protocol(
        J, users, timesteps, reps, _SD_protocol, nodes=True, count_fusion=count_fusion
    )
    update_usage_from_subgraph(G, J)
    return er, multipartite_gen_time, avg_links_used

def _run_protocol(G, users, timesteps, reps, success_protocol, nodes=False, count_fusion=False):
    reset_graph_usage(G)
    links_used = 0

    # Track entanglement generation times
    multipartite_gen_time = -1 * np.ones(reps)  # Initialize as -1 for all reps

    for i in range(reps):
        reset_graph_state(G)
        used_nodes = []
        t = 0

        while t < timesteps and multipartite_gen_time[i] == -1:  # Run for timesteps or until success
            t += 1
            run_entanglement_step(G, used_nodes, nodes)
            H = get_entangled_subgraph(G)
            success = success_protocol(G, H, users, used_nodes, count_fusion)

            if success:
                multipartite_gen_time[i] = t  # Record success time
                links_used += sum(path["edge_count"] for path in used_nodes)

    rate = _multipartite_rate(multipartite_gen_time, timesteps)
    update_graph_usage(G, reps)
    avg_links_used = links_used / reps if reps > 0 else 0
    return rate, multipartite_gen_time, avg_links_used


def _SD_protocol(G, H, users, used_nodes, count_fusion=False):
    source_node = users[0]
    destination_nodes = users[1:]

    for destination_node in destination_nodes:
        if not G.nodes[destination_node]["entangled"] and nx.has_path(
            H, source_node, destination_node
        ):
            path = nx.shortest_path(H, source_node, destination_node)
            _create_bell_pair(G, H, path, used_nodes)
    return all([G.nodes[x]["entangled"] for x in destination_nodes])


def _create_bell_pair(G, H, path, used_nodes):
    """
    create Bell pair between source node and destination node, record as value "entangled" in destination node in graph G. This is done by performing entanglement swapping at all nodes in the shortest path

    Inputs:
    G                - Networkx graph G(V,E') which defines the topology of the graph (or subgraph which entanglement is attempted on).
    H                - Networkx graph G'(V,E') which defines the topology of the links.
    route            - path of nodes selected to perform entanglement swapping between route[0]=source route[-1] = destination
    used_nodes       - list of paths of the nodes that performed entanglement swapping to be updated

    """
    for u, v in zip(path[:-1], path[1:]):  # node - next_node pairs
        H.remove_edge(u, v)
        edge = G.edges[u, v]
        edge["entangled"] = False
        edge["age"] = 0

    destination_node = G.nodes[path[-1]]
    destination_node["entangled"] = True
    destination_node["age"] = 0

    used_nodes.append(
        {"nodes": path[1:-1], "age": 0, "destination_node": path[-1], "edge_count": len(path) - 1}
    )


def _multipartite_rate(gen_times, max_timesteps):
    """
    Returns entanglement rate (ER) in terms of GHZ/timeslots and the total timesteps.

    Parameters:
    gen_times (list or array): Array of timesteps until successful GHZ generation; -1 if no GHZ generated.
    max_timesteps (int): Maximum number of timesteps attempted.

    Returns:
    float: Entanglement rate (GHZs generated per timestep).
    """
    # Ensure gen_times is a NumPy array
    gen_times = np.atleast_1d(gen_times)

    # Filter successful attempts
    successful_attempts = gen_times[gen_times != -1]

    # Handle edge case where no successful attempts
    fail_count = len(gen_times) - len(successful_attempts)
    t_total = (
        sum(successful_attempts) + fail_count * max_timesteps
        if len(successful_attempts) > 0
        else max_timesteps * len(gen_times)
    )

    return len(successful_attempts) / t_total if t_total > 0 else 0.0



def _get_star(G, users):
    """
    get edge disjoint shortest paths from set source (first node in list)

        Input Pararmeters:
        G      - Networkx graph G(V,E) which defines the topology of the network. see graphs.py for more details
        users  - List of nodes in G which between which a GHZ should be shared. users[0] is the centre of the star which should be calculated before sending to SP_protocol
        Outputs:
        J      - Networkx graph J(V,E') with edges of the star-path connecting each destination user with the source node

    Notes:
    non-optimal star found ? #
    if no edge-disjoint star-route exists, then allow edge sharing (this is none edge disjoint and will give ER = 0 if Qc = 1. If Qc>1 then protocol feasible as time division multiplexing (TDM) allows bell pairs to be generated
    TODO redo this function ES - 17/11/2022
    """

    # get edge disjoint shortest paths from set source (first node in list)
    # if edge disjoint paths don't exist, allow shared edge use
    # NON optimal good enough for grids with corner users
    source_node = users[0]
    destination_nodes = users[1:]
    # copy G twice H for calculation and J for reduced graph
    T = G.__class__()
    T.add_nodes_from(G.nodes(data=True))
    T.add_edges_from(G.edges(data=True))
    # Graph H is a deepcopy of G, if an edge is added to J it is removed from H, routing is then performed over H. This enforces edge disjoint routing
    J = G.__class__()
    J.add_nodes_from(G.nodes(data=True))  # Graph J with nodes from G and no edges (yet!)
    edge_disjoint = True  # G.degree[source_node]>= len(destination_nodes) # can it be edge disjoint
    for destination_node in destination_nodes:
        if nx.has_path(T, source_node, destination_node):
            path = nx.shortest_path(T, source_node, destination_node)
            for u, v in zip(path[:-1], path[1:]):  # node- next_node pairs
                T.remove_edge(u, v)  # remove path from H
                J.add_edge(u, v)  # add edge to new graph J
        else:
            edge_disjoint = False  # unused flag to say if J is edge_disjoint
            path = nx.shortest_path(G, source_node, destination_node)
            for u, v in zip(path[:-1], path[1:]):
                J.add_edge(u, v)  # add edge to new graph J
                if T.has_edge(u, v):
                    T.remove_edge(u, v)  # remove path from H
    [
        J[u][v].update(G.get_edge_data(u, v)) for (u, v) in J.edges()
    ]  # add edge data to edge in J from G
    return J

initialize()
mean_interarrival = 5.0  # Example values
mean_service = 3.0
num_delays_required = 0


def calculate_blocking_rate(total_requests, successful_requests):
    """
    Calculates the blocking rate of the quantum network.

    Parameters:
    total_requests (int): Total number of entanglement requests.
    successful_requests (int): Number of successful entanglement requests.

    Returns:
    float: Blocking rate (0 to 1), where 1 means all requests are blocked.
    """
    if total_requests == 0:
        return 0.0  # Avoid division by zero; no requests mean no blocking
    return 1 - (successful_requests / total_requests)

def check_node_availability(G, new_users, entangled_requests):
    """
    Check if the nodes in the new request are available (not currently used in active entanglement).

    Parameters:
    G (Graph): The quantum network graph.
    new_users (list): Nodes involved in the new entanglement request.
    entangled_requests (list): List of active entanglement requests.

    Returns:
    bool: True if nodes are available (no collision), False otherwise.
    """
    active_nodes = set()  # Create a set to store all active nodes currently involved in entanglement

    # Add nodes from each active request to the active_nodes set
    for req in entangled_requests:
        active_nodes.update(req[0])

    # Check if any new request node is already active
    for node in new_users:
        if node in active_nodes:
            return False

    return True

def release_resources(G, users):
    """
    Release entangled resources associated with a completed request.
    Only the nodes involved in the specific request are reset.
    """
    for node in users:
        G.nodes[node]["entangled"] = False  # Mark node as not entangled
        G.nodes[node]["age"] = 0            # Reset the age of the node


def dynamic_simulation(graph_size=(3, 3), mean_interarrival=10.0, mean_service=3.0,
                       max_requests=100, collect_stats=False, entanglement_prob=0.1):
    """
    Simulates a dynamic quantum network using the SP_protocol with dynamic event management.

    Parameters:
        graph_size (tuple): Dimensions of the quantum network grid (rows, cols).
        mean_interarrival (float): Mean time between request arrivals (exponential distribution).
        mean_service (float): Mean service time before an entangled request departs.
        max_requests (int): Maximum number of requests to process before stopping the simulation.
        collect_stats (bool): If True, returns total and successful requests; otherwise, only prints results.
        entanglement_prob (float): Probability of entanglement between nodes in the quantum network.

    Returns:
        tuple: (total_requests, successful_requests) if collect_stats is True, otherwise None.

    The simulation follows these steps:
    1. Initializes the quantum network and simulation parameters.
    2. Processes arrivals and departures using an event-driven model.
    3. Tracks entanglement request successes and failures.
    4. Calculates the blocking rate at the end of the simulation.
    """
    MAX_CONCURRENT_REQUESTS = 5  # Defines the maximum number of concurrent entangled requests allowed

    # Set the global mean interarrival time for request generation
    Initialisation.mean_interarrival = mean_interarrival

    # Initialize the quantum network graph with given dimensions and entanglement probability
    G = Initialisation.initialize_quantum_network(*graph_size, p=entanglement_prob)

    # Perform necessary initialization for simulation
    initialize()

    sim_clock = 0.0  # Simulation clock to track the current simulation time
    next_arrival_time = expon(mean_interarrival)  # Schedule the first request arrival event
    next_departure_time = float('inf')  # Initially, no departures are scheduled

    entangled_requests = []  # List to track ongoing entangled requests and their departure times
    total_requests = 0  # Counter for total requests made in the simulation
    successful_requests = 0  # Counter for successfully completed requests

    # Continue the simulation until the maximum number of requests is reached
    while total_requests < max_requests:
        # Process departures before new arrivals if necessary
        while next_departure_time <= next_arrival_time:
            sim_clock = next_departure_time  # Advance the simulation clock to the next departure event
            if entangled_requests:  # If there are ongoing entangled requests, process one
                completed_request = entangled_requests.pop(0)  # Remove the first completed request
                release_resources(G, completed_request[0])  # Release network resources used by the request
            # Update next departure time to the soonest remaining request departure
            next_departure_time = min((req[1] for req in entangled_requests), default=float('inf'))

        # Process a new request arrival event
        sim_clock = next_arrival_time  # Move simulation clock to next arrival event
        next_arrival_time += expon(mean_interarrival)  # Schedule next request arrival

        # Select a random center node and users in the network
        center_node = random.choice(list(G.nodes))  # Pick a random node as the central node
        users = random.sample(list(G.nodes - {center_node}), k=random.randint(3, 4))  # Select 3 or 4 random user nodes

        # Check if the selected nodes are available for entanglement
        if check_node_availability(G, users, entangled_requests):
            if len(entangled_requests) < MAX_CONCURRENT_REQUESTS:  # Enforce resource constraints
                # Run the SP_protocol to attempt entanglement
                rate, gen_time, avg_links_used = SP_protocol(
                    G, users, timesteps=1000, reps=1, count_fusion=False
                )

                if gen_time > 0:  # If entanglement was successful
                    successful_requests += 1  # Increment successful request counter
                    departure_time = sim_clock + expon(mean_service)  # Compute departure time for this request
                    entangled_requests.append((users, departure_time))  # Track the request and its departure time
                    next_departure_time = min(req[1] for req in entangled_requests)  # Update next departure event

        total_requests += 1  # Increment total request count

    # Compute the blocking rate (ratio of failed requests)
    blocking_rate = calculate_blocking_rate(total_requests, successful_requests)

    # Print summary of simulation results
    print("\nSimulation Complete")
    print(f"Total Requests: {total_requests}")
    print(f"Successful Requests: {successful_requests}")
    print(f"Blocking Rate: {blocking_rate:.2f}")

    # If statistics collection is enabled, return the total and successful requests
    if collect_stats:
        return total_requests, successful_requests
    else:
        return None

if __name__ == "__main__":
    dynamic_simulation(graph_size=(3, 3), max_requests=1000)



