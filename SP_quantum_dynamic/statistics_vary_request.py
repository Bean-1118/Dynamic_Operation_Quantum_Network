import numpy as np
import matplotlib.pyplot as plt
from simulation_NEW_1 import dynamic_simulation, calculate_blocking_rate


def generate_statistics():
    """
    Generates statistics for the quantum network simulation by varying different parameters
    while considering different request numbers (1000, 10000, 100000) in a single diagram.

    The function performs the following tasks:
    1. Varies mean interarrival time while keeping service time fixed, and plots
       Blocking Rate vs. Traffic Load with three different request sizes.
    2. Varies mean service time while keeping interarrival time fixed, and plots
       Blocking Rate vs. Traffic Load with three different request sizes.
    3. Varies entanglement probability while keeping both mean interarrival and
       mean service time fixed, and plots Blocking Rate vs. Probability.

    Returns:
        None: The function generates plots but does not return any values.
    """
    request_values = [1000, 10000, 100000]  # Different max request numbers
    colors = ['green', 'red', 'blue']  # Colors for each request scenario
    labels = ['1000 requests', '10000 requests', '100000 requests']
3
    fixed_service_time = 3.0
    fixed_interarrival_time = 5.0
    fixed_probability = 0.5
    graph_Size = (6, 6)

    # === 1. Varying Mean Interarrival Time ===
    interarrival_times = np.linspace(2, 15, 10)
    plt.figure(figsize=(10, 6))

    for i, max_requests in enumerate(request_values):
        blocking_rates_interarrival = []

        for interarrival in interarrival_times:
            total_requests, successful_requests = dynamic_simulation(
                graph_size=graph_Size,
                mean_interarrival=interarrival,
                mean_service=fixed_service_time,
                max_requests=max_requests,
                collect_stats=True,
                entanglement_prob=fixed_probability
            )

            blocking_rate = calculate_blocking_rate(total_requests, successful_requests)
            blocking_rates_interarrival.append(blocking_rate)

        traffic_load_interarrival = [fixed_service_time / inter for inter in interarrival_times]
        plt.plot(traffic_load_interarrival, blocking_rates_interarrival, marker='o', linestyle='-',
                 color=colors[i], label=labels[i])

    plt.xscale("log")
    plt.xlabel("Traffic Load (Service Time / Interarrival Time)",fontsize=18)
    plt.ylabel("Blocking Rate",fontsize=18)
    plt.title("Blocking Rate vs. Traffic Load (Varying Interarrival Time)",fontsize=20,fontweight='bold')
    plt.legend()
    plt.grid()
    plt.show()

    # === 2. Varying Mean Service Time ===
    service_times = np.linspace(1, 10, 10)
    plt.figure(figsize=(10, 6))

    for i, max_requests in enumerate(request_values):
        blocking_rates_service = []

        for service in service_times:
            total_requests, successful_requests = dynamic_simulation(
                graph_size=graph_Size,
                mean_interarrival=fixed_interarrival_time,
                mean_service=service,
                max_requests=max_requests,
                collect_stats=True,
                entanglement_prob=fixed_probability
            )

            blocking_rate = calculate_blocking_rate(total_requests, successful_requests)
            blocking_rates_service.append(blocking_rate)

        traffic_load_service = [serv for serv in service_times / fixed_interarrival_time]
        plt.plot(traffic_load_service, blocking_rates_service, marker='s', linestyle='-',
                 color=colors[i], label=labels[i])

    plt.xscale("log")
    plt.xlabel("Traffic Load (Service Time / Interarrival Time)",fontsize=18)
    plt.ylabel("Blocking Rate",fontsize=18)
    plt.title("Blocking Rate vs. Traffic Load (Varying Service Time)",fontsize=20,fontweight='bold')
    plt.legend()
    plt.grid()
    plt.show()

    # === 3. Varying Entanglement Probability ===
    probabilities = np.linspace(0.1, 1.0, 10)
    plt.figure(figsize=(10, 6))

    for i, max_requests in enumerate(request_values):
        blocking_rates_probability = []

        for prob in probabilities:
            total_requests, successful_requests = dynamic_simulation(
                graph_size=graph_Size,
                mean_interarrival=fixed_interarrival_time,
                mean_service=fixed_service_time,
                max_requests=max_requests,
                collect_stats=True,
                entanglement_prob=prob
            )

            blocking_rate = calculate_blocking_rate(total_requests, successful_requests)
            blocking_rates_probability.append(blocking_rate)

        plt.plot(probabilities, blocking_rates_probability, marker='^', linestyle='-',
                 color=colors[i], label=labels[i])

    plt.xlabel("Entanglement Probability",fontsize=18)
    plt.ylabel("Blocking Rate",fontsize=18)
    plt.title("Blocking Rate vs. Entanglement Probability",fontsize=20,fontweight='bold')
    plt.legend()
    plt.grid()
    plt.show()


if __name__ == "__main__":
    generate_statistics()
