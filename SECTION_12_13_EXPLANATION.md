# Queuechella Simulation: Sections 12 & 13 Explanation

This document explains the core engine of the Queuechella Simulation, which is divided into **Section 12 (Events)** and **Section 13 (Simulation)**. These sections contain the Object-Oriented Event-Driven logic that powers the entire festival.

---

## Section 12: Events (אירועים)
Instead of using a traditional while loop that checks every entity every minute, this simulation is built on the **Discrete-Event Simulation (DES)** paradigm. The Event base class allows us to schedule specific actions to happen at exact timestamps in the future.

We created several distinct event types that inherit from Event to represent everything that can happen at the festival:

### 1. Arrivals (Group A)
- **SingleArrival, CoupleArrival, FriendsGroupArrival**: These events trigger when new visitors arrive at the festival. They immediately schedule the *next* arrival of that type based on the statistical distributions (Exponential/Uniform), and then send the new visitors to the Entry gate.

### 2. Service & Stage Transitions (Group B)
- **ShowStart_* & ShowEnd_***: These handle the scheduled Main and Side stage shows. When a show starts, it admits waiting guests from the queue up to its capacity. When it ends, it releases them and schedules the next show.
- **EndService_***: When a visitor finishes an activity (Photo, Charging, Merch, BodyArt), this event frees the server (artist/clerk/charger) so the next person in line can use it. It then routes the finished visitor to their next desired activity based on their itinerary.
- **EndAtDJstage**: A continuous-admission event for the DJ stage.
- **EndOrder_FoodCourt, EndPrep_FoodCourt, EndEating_FoodCourt**: A multi-step sequence that routes hungry guests from ordering, to waiting for food preparation, to eating.

### 3. Queue Abandonment (Group C)
- **AbandonQueue**: When a group joins a queue for a service station, this event is scheduled in the future (15 minutes for Friends, 20 minutes for Couples/Singles). If the group is still waiting when the timer goes off, this event pulls them out of the line, deducts their satisfaction points, and routes them elsewhere.

### 4. Special Time-Bound Events (Group D & E)
- **EarlyExitCheck**: Evaluates if a guest at the back of the Main Stage crowd decides to leave early.
- **BreakEnd_BodyArt**: Wakes the artist up after their mandatory 15-minute break.
- **EndOfDay1 & Day2Start**: Handles the overnight transition, freezing active queues when the festival closes at 20:00 and waking everyone back up the next morning at 09:00.
- **EndOfStay**: Triggers when a guest finishes their entire itinerary and officially leaves the festival.

---

## Section 13: The Simulation Engine (מחלקת הסימולציה)
The Simulation class is the central orchestrator that holds everything together. It contains the **Future Event List (FEL)**, which is implemented as a Priority Queue (Heap). 

### Key Responsibilities:
1. **Initialization (__init__)**: 
   - It sets up all the festival venues (Stages, Food Court, Merch, etc.) with their designated capacities and servers.
   - It hooks up the statistical Sampler and the KPITracker.
2. **Scheduling (schedule)**: 
   - Takes an Event object and inserts it into the Priority Queue, perfectly sorted by its scheduled timestamp.
3. **Routing (	ry_admit & dvance_itinerary_or_exit)**: 
   - A centralized routing hub that decides where a visitor goes next. If a venue is full, 	ry_admit seamlessly drops them into its queue.
4. **The Main Loop (
un)**: 
   - The heart of the simulation! It pops the earliest event from the priority queue, advances the master clock (self.time) to that exact moment, and calls event.execute(self). 
   - It repeats this instantly and efficiently until the clock hits the end of Day 2 (1980 minutes), processing tens of thousands of individual events in just a few seconds.

By separating the **What happens** (Section 12 Events) from the **When it happens** (Section 13 Simulation loop), the code is highly modular, efficient, and easily extensible for testing the required Alternatives!
