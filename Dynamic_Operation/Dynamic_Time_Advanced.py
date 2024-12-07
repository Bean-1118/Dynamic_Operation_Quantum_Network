import math
import random

# Constants
Q_LIMIT = 100  # Limit on queue length
BUSY = 1       # Mnemonics for server's being busy
IDLE = 0       # Mnemonics for server's being idle

# Global variables
next_event_type = 0 # type of the next event to occur. (arrival event or departure event)
num_custs_delayed = 0 # Tracks the total number of customers who have been delayed (served after waiting in the queue)
num_delays_required = 0 # The total number of customers to simulate (stopping condition for the simulation)
num_events = 0 # The total number of distinct event types in the system (always 2 for each)
num_in_q = 0 # The current number of customers waiting in the queue (not yet being served)
server_status = IDLE # Tracks the server's current state

area_num_in_q = 0.0 # Accumulates the area under the "number-in-queue" curve over time -> Used to calculate the average number of customers in the queue
area_server_status = 0.0 # Accumulates the area under the "server status" curve over time -> Used to calculate the server utilization (proportion of time the server is busy)
mean_interarrival = 0.0
mean_service = 0.0
sim_time = 0.0 # The current time in the simulation
time_arrival = [0.0] * (Q_LIMIT + 1) # An array that stores the arrival times of customers currently in the queue
time_last_event = 0.0 # The time at which the last event occurred
time_next_event = [0.0] * 3
total_of_delays = 0.0 # Sum of all customer delays in the queue (waiting time)

# Input and output files (use placeholders for now)
infile = None
outfile = None
def initialize():
    """Initialization function for the simulation."""
    global sim_time, server_status, num_in_q, time_last_event
    global num_custs_delayed, total_of_delays, area_num_in_q, area_server_status
    global time_next_event

    # Initialize the simulation clock
    sim_time = 0.0

    # Initialize the state variables
    server_status = IDLE
    num_in_q = 0
    time_last_event = 0.0

    # Initialize the statistical counters
    num_custs_delayed = 0
    total_of_delays = 0.0
    area_num_in_q = 0.0
    area_server_status = 0.0

    # Initialize the event list
    time_next_event[1] = sim_time + expon(mean_interarrival)
    time_next_event[2] = 1.0e30


def timing():
    """Timing function to determine the next event."""
    global next_event_type, sim_time, time_next_event

    # Initialize variables
    min_time_next_event = 1.0e29
    next_event_type = 0

    # Determine the event type of the next event to occur
    for i in range(1, num_events + 1):  # Adjusted for Python's 0-based indexing
        if time_next_event[i] < min_time_next_event:
            min_time_next_event = time_next_event[i]
            next_event_type = i

    # Check if the event list is empty
    if next_event_type == 0:
        # The event list is empty, so stop the simulation
        print(f"\nEvent list empty at time {sim_time}")
        exit(1)

    # The event list is not empty, so advance the simulation clock
    sim_time = min_time_next_event

def arrive():
    """Arrival event function."""
    global sim_time, time_next_event, server_status, num_in_q, num_custs_delayed, total_of_delays
    global time_arrival, mean_interarrival, mean_service

    # Schedule next arrival
    time_next_event[1] = sim_time + expon(mean_interarrival)

    # Check to see whether the server is busy
    if server_status == BUSY:
        # Server is busy, so increment number of customers in queue
        num_in_q += 1

        # Check for overflow condition
        if num_in_q > Q_LIMIT:
            # The queue has overflowed, so stop the simulation
            print("\nOverflow of the array time_arrival")
            print(f"Time {sim_time}")
            exit(2)

        # There is still room in the queue, store the arrival time
        time_arrival[num_in_q] = sim_time
    else:
        # Server is idle, arriving customer has a delay of zero
        delay = 0.0
        total_of_delays += delay

        # Increment the number of customers delayed and make server busy
        num_custs_delayed += 1
        server_status = BUSY

        # Schedule departure (service completion)
        time_next_event[2] = sim_time + expon(mean_service)

def depart():
    """Departure event function."""
    global num_in_q, server_status, time_next_event, sim_time, total_of_delays
    global num_custs_delayed, time_arrival, mean_service

    # Check to see whether the queue is empty
    if num_in_q == 0:
        # The queue is empty, so make the server idle and eliminate the departure event
        server_status = IDLE
        time_next_event[2] = 1.0e30
    else:
        # The queue is nonempty, so decrement the number of customers in the queue
        num_in_q -= 1

        # Compute the delay of the customer who is beginning service
        delay = sim_time - time_arrival[1]
        total_of_delays += delay

        # Increment the number of customers delayed and schedule departure
        num_custs_delayed += 1
        time_next_event[2] = sim_time + expon(mean_service)

        # Move each customer in the queue (if any) up one place
        for i in range(1, num_in_q + 1):  # Adjusted for Python's 0-based indexing
            time_arrival[i] = time_arrival[i + 1]

def report():
    """Report generator function."""
    global total_of_delays, num_custs_delayed, area_num_in_q, sim_time, area_server_status

    # Compute and write estimates of desired measures of performance
    average_delay = total_of_delays / num_custs_delayed if num_custs_delayed > 0 else 0.0
    average_num_in_queue = area_num_in_q / sim_time if sim_time > 0 else 0.0
    server_utilization = area_server_status / sim_time if sim_time > 0 else 0.0

    print(f"\nAverage delay in queue: {average_delay:11.3f} minutes")
    print(f"Average number in queue: {average_num_in_queue:10.3f}")
    print(f"Server utilization: {server_utilization:15.3f}")
    print(f"Time simulation ended: {sim_time:12.3f} minutes")


def update_time_avg_stats():
    """Update area accumulators for time-average statistics."""
    global sim_time, time_last_event, num_in_q, server_status
    global area_num_in_q, area_server_status

    # Compute time since last event and update last-event-time marker
    time_since_last_event = sim_time - time_last_event
    time_last_event = sim_time

    # Update area under number-in-queue function
    area_num_in_q += num_in_q * time_since_last_event

    # Update area under server-busy indicator function
    area_server_status += server_status * time_since_last_event

def expon(mean):
    """Exponential variate generation function.

    Returns an exponential random variate with the specified mean.
    """
    return -mean * math.log(random.random())


# Simulation parameters
mean_interarrival = 0.0
mean_service = 0.0
num_delays_required = 0

def main():
    global mean_interarrival, mean_service, num_delays_required, num_events

    # Open input and output files
    infile = open("mm1in.txt", "r")
    outfile = open("mm1out.txt", "w")

    # Specify the number of events for the timing function
    num_events = 2  # 1: Arrival, 2: Departure

    # Read input parameters
    input_data = infile.readline().strip().split()
    mean_interarrival = float(input_data[0]) # The average time between consecutive customer arrivals (input parameter)
    mean_service = float(input_data[1]) # The average time it takes to serve a customer (input parameter)
    num_delays_required = int(input_data[2]) # The total number of customers to simulate (stopping condition for the simulation).

    # Write report heading and input parameters
    outfile.write("Single-server queueing system\n\n")
    outfile.write(f"Mean interarrival time: {mean_interarrival:11.3f} minutes\n")
    outfile.write(f"Mean service time: {mean_service:16.3f} minutes\n")
    outfile.write(f"Number of customers: {num_delays_required:14d}\n\n")

    # Initialize the simulation
    initialize()

    # Run the simulation while more delays are still needed
    while num_custs_delayed < num_delays_required:
        # Determine the next event
        timing()

        # Update time-average statistical accumulators
        update_time_avg_stats()

        # Invoke the appropriate event function
        if next_event_type == 1:  # Arrival event
            arrive()
        elif next_event_type == 2:  # Departure event
            depart()

    # Invoke the report generator and end the simulation
    report()

    # Close the files
    infile.close()
    outfile.close()

# Run the simulation
if __name__ == "__main__":
    main()

