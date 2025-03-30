import numpy as np
import matplotlib.pyplot as plt
from simulation_NEW_1 import dynamic_simulation, calculate_blocking_rate


def generate_statistics():
    """
    Generates statistics for the quantum network simulation by varying different parameters
    and plotting the blocking rate against traffic load and entanglement probability.

    The function performs the following tasks:
    1. Varies mean interarrival time while keeping service time fixed, and plots
       Blocking Rate vs. Traffic Load (Top Graph).
    2. Varies mean service time while keeping interarrival time fixed, and plots
       Blocking Rate vs. Traffic Load (Bottom Graph).
    3. Varies entanglement probability while keeping both mean interarrival and
       mean service time fixed, and plots Blocking Rate vs. Probability in a
       separate window.

    The maximum number of requests for each test is fixed at 1000.

    Returns:
        None: The function generates plots but does not return any values.
    """
    max_requests = 10000 # Fixed max requests for all simulations
    fixed_service_time = 3.0
    fixed_interarrival_time = 5.0
    fixed_probability = 0.5
    graph_Size = (3,3)

    # Varying mean interarrival time (Top Graph)
    interarrival_times = np.linspace(2, 15, 10)  #

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

        print(
            f"Interarrival Time: {interarrival}, Total: {total_requests}, Successful: {successful_requests}, Blocking Rate: {blocking_rate}")

        if total_requests > 0:  # Ensure that simulation ran before appending
            blocking_rates_interarrival.append(blocking_rate)
        else:
            print(f"⚠ Warning: No requests processed for Interarrival Time {interarrival}")

    print(f"Final Blocking Rates Collected: {len(blocking_rates_interarrival)} expected: {len(interarrival_times)}")

    # Varying mean service time (Bottom Graph)
    service_times = np.linspace(1, 10, 10)
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

        print(
            f"Service Time: {service}, Total: {total_requests}, Successful: {successful_requests}, Blocking Rate: {blocking_rate}")

        # Ensure only 10 values are added
        if total_requests > 0 and len(blocking_rates_service) < len(service_times):
            blocking_rates_service.append(blocking_rate)
        else:
            print(f"⚠ Warning: Service time loop may be running extra iterations.")

    # Plot Blocking Rate vs. Traffic Load (First Window)
    traffic_load_interarrival = [fixed_service_time / inter for inter in interarrival_times]
    traffic_load_service = [serv for serv in service_times / fixed_interarrival_time]

    # Testing
    print(f"Interarrival: {interarrival}, Total: {total_requests}, Successful: {successful_requests}")

    if not blocking_rates_interarrival:
        print("Error: No data collected for Blocking Rate vs. Traffic Load (Interarrival Time).")
        return

    plt.figure(figsize=(10, 8))

    # Top Graph: Varying Interarrival Time
    plt.subplot(2, 1, 1)
    plt.plot(traffic_load_interarrival, blocking_rates_interarrival, marker='o', linestyle='-')
    plt.xscale("log")
    plt.xlabel("Traffic Load (Service Time / Interarrival Time)",fontsize=18)
    plt.ylabel("Blocking Rate",fontsize=18)
    plt.title("Blocking Rate vs. Traffic Load (Varying Interarrival Time)",fontsize=20,fontweight='bold')
    # Increase tick font size
    plt.xticks(fontsize=14)
    plt.yticks(fontsize=14)

    # Bottom Graph: Varying Service Time
    plt.subplot(2, 1, 2)
    plt.plot(traffic_load_service, blocking_rates_service, marker='s', linestyle='-')
    plt.xscale("log")
    plt.xlabel("Traffic Load (Service Time / Interarrival Time )",fontsize=18)
    plt.ylabel("Blocking Rate",fontsize=18)
    plt.title("Blocking Rate vs. Traffic Load (Varying Service Time)",fontsize=20,fontweight='bold')
    # Increase tick font size
    plt.xticks(fontsize=14)
    plt.yticks(fontsize=14)

    plt.tight_layout()
    plt.show()

    # Varying Probability (Second Window)
    probabilities = np.linspace(0.1, 1.0, 10)  # Example range

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

        print(
            f"Probability: {prob}, Total: {total_requests}, Successful: {successful_requests}, Blocking Rate: {blocking_rate}")

        if total_requests > 0 and len(blocking_rates_probability) < len(probabilities):
            blocking_rates_probability.append(blocking_rate)

    # Plot Blocking Rate vs. Probability (Second Window)
    plt.figure(figsize=(8, 6))
    plt.plot(probabilities, blocking_rates_probability, marker='^', linestyle='-')
    plt.xlabel("Entanglement Probability",fontsize=18)
    plt.ylabel("Blocking Rate",fontsize=18)
    plt.title("Blocking Rate vs. Entanglement Probability",fontsize=20,fontweight='bold')
    # Increase tick font size
    plt.xticks(fontsize=14)
    plt.yticks(fontsize=14)
    plt.show()


if __name__ == "__main__":
    generate_statistics()
