import simpy
import numpy as np
import random

NUM_WORKSTATIONS = 6
NUM_BINS = 3
BIN_CAPACITY = 25
PROB_FAIL_MEAN = [0.22, 0.11, 0.17, 0.06, 0.08, 0.11] #CHANGE THIS LINE FOR EXAM, JUST CHANGE TO THE NEW PROBABILITIES
PROB_FAIL_STD = 0.03
PROB_REJECTION = 0.05
PROB_ACCIDENT = 0.0001
AVERAGE_FIX_TIME = 3
AVERAGE_WORK_TIME = 4

SIM_TIME = 500
NUM_MONTHS = 1

class ManufacturingFacility:
    def __init__(self, env):
        self.env = env
        self.workstations = [simpy.Resource(env, capacity=1) for _ in range(NUM_WORKSTATIONS)]
        self.bins = [simpy.Container(env, capacity=BIN_CAPACITY, init=BIN_CAPACITY) for _ in range(NUM_BINS)]
        self.supplier = simpy.Container(env, capacity=BIN_CAPACITY * NUM_WORKSTATIONS * NUM_BINS,
                                         init=BIN_CAPACITY * NUM_WORKSTATIONS * NUM_BINS)
        self.production_count = 0
        self.total_fix_time = 0
        self.total_delay_time = 0
        self.total_rejections = 0
        self.total_accidents = 0
        self.workstation_occupancy = [0] * NUM_WORKSTATIONS
        self.workstation_downtime = [0] * NUM_WORKSTATIONS
        self.supplier_occupancy = 0

    def produce(self):
        while True:
            # Get a bin of raw materials
            with self.supplier.get(BIN_CAPACITY * NUM_WORKSTATIONS) as bin:

                start_time = round(self.env.now, 2)#registra el tiempo
                yield self.env.timeout(np.random.normal(AVERAGE_WORK_TIME)*0.5) #CHANGE LINE FOR THE EXAM, I JUST MULTIPLY THE TIME PER 0.5

                # Check for accidents
                if np.random.random() < PROB_ACCIDENT:
                    self.total_accidents += 1
                    yield self.env.timeout(100)  # Simulate a halt in production for 100 time units

                for i in [0, 1, 2, 4, 3, 5]:  # CHANGE LINE FOR THE EXAM, USE A NEW ORDER
                    workstation = self.workstations[i] #CHANGE LINE FOR THE EXAM

                    # Get a workstation
                    with workstation.request() as req:
                        yield req

                        # Calculate probability of failure for this workstation
                        prob_fail = max(0, min(1, np.random.normal(PROB_FAIL_MEAN[i], PROB_FAIL_STD)))

                        # Check for workstation failure
                        if random.random() < prob_fail:
                            self.total_fix_time += round(np.random.exponential(AVERAGE_FIX_TIME), 2)
                            self.workstation_downtime[i] += round(np.random.exponential(AVERAGE_FIX_TIME), 2)
                            yield self.env.timeout(np.random.exponential(AVERAGE_FIX_TIME))
                            #print(f"Product stopped at workstation {i+1} at time {round(self.env.now, 2)} due to failure")

                        # Simulate work at workstation
                        yield self.env.timeout(np.random.normal(AVERAGE_WORK_TIME))
                        self.workstation_occupancy[i] += 1

                        # Print message indicating product and workstation
                        end_time = round(self.env.now, 2)
                        #print(f"Product at workstation {i+1} finished at time {end_time}, took {round(end_time - start_time, 2)} units")


                # Check for rejection
                if np.random.random() < PROB_REJECTION:
                    self.total_rejections += 1
                    continue  # Skip further processing if rejected

                # End of production process
                end_time = round(self.env.now, 2)
                self.production_count += 1
                self.total_delay_time += round((end_time - start_time), 2)
                print(f"Product finished at time {end_time}, took {round(end_time - start_time, 2)} units")

def run_simulation():
    production_results = []
    fix_times = []
    delays_due_to_bottleneck = []
    rejections = []
    accidents = []

    for _ in range(NUM_MONTHS):
        # Setup and start the simulation
        env = simpy.Environment()
        facility = ManufacturingFacility(env)
        env.process(facility.produce())

        env.run(until=SIM_TIME)

        # Store results for analysis
        production_results.append(facility.production_count)
        fix_times.append(facility.total_fix_time)
        delays_due_to_bottleneck.append(facility.total_delay_time)
        rejections.append(facility.total_rejections)
        accidents.append(facility.total_accidents)

    # Calculate averages and statistics for a month
    avg_production_month = round(np.mean(production_results), 2)
    avg_rejections_month = round(np.mean(rejections), 2)
    avg_fix_time_month = round(np.mean(fix_times), 2)
    avg_delay_due_to_bottleneck_month = round(np.mean(delays_due_to_bottleneck), 2)
    avg_accidents_month = round(np.mean(accidents), 2)

    # Calculate average occupancy and downtime for each workstation for a month
    avg_occupancy_month = [round(occ / (NUM_WORKSTATIONS * NUM_MONTHS), 2) for occ in facility.workstation_occupancy]
    avg_downtime_month = [round(downtime / NUM_MONTHS, 2) for downtime in facility.workstation_downtime]


    #CHANGE THIS LINE TO CALCULATE AVRG FOR THE DOWTIME
    avr_dowtime = 0.0
    for i in avg_downtime_month:
        avr_dowtime = avr_dowtime + i
    avr_dowtime = avr_dowtime / NUM_WORKSTATIONS

    print("------------MONTH EXPECTATIONS--------------")
    print(f"Average production for a month: {avg_production_month}")
    print(f"Average quality failures per month: {avg_rejections_month}")
    print(f"Average occupancy for each workstation for a month: {avg_occupancy_month}")
    print(f"Average downtime for each workstation for a month: {avg_downtime_month}")
    print(f"Average fix time in all the plant for a month: {avg_fix_time_month}")
    print(f"Average accidents per month: {avg_accidents_month}")
    print(f"Average downtime all workstations: {avr_dowtime}")


if __name__ == "__main__":
    run_simulation()
