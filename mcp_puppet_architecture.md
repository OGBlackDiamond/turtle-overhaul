# MCP as Puppet Master: Orchestration Architecture

The core mental model shift is this: **turtles have no opinions, only capabilities**. Every decision — including micro-decisions like "should I turn left or right" — lives in the MCP. The turtle is just an async executor of whatever the MCP hands it.

---

## The Three Layers

```
┌─────────────────────────────────────────────────────┐
│                      MCP                           │
│  ┌─────────────────┐    ┌───────────────────────┐  │
│  │  Utility Scorer  │    │  Job Scheduler        │  │
│  │  (what to do)   │    │  (how/when to do it)  │  │
│  └────────┬────────┘    └──────────┬────────────┘  │
│           └──────────┬─────────────┘               │
│                ┌─────▼──────┐                       │
│                │ Job Queue  │  ← MCP can inject     │
│                │ per turtle │    at any priority    │
│                └─────┬──────┘                       │
└──────────────────────┼──────────────────────────────┘
                       │  (job)
┌──────────────────────▼──────────────────────────────┐
│                   Turtle                            │
│         Executes steps. Reports results.            │
│         No decisions. Pure capability.              │
└─────────────────────────────────────────────────────┘
```

---

## The Job Object

A `Job` is the unit of work the MCP assigns. It's a named, prioritized, preemptable sequence of `Step`s.

```python
@dataclass
class Step:
    command: str          # e.g. "turtle.forward()", "turtle.dig()"
    expected: str | None  # expected return value, for validation
    on_fail: str          # "retry" | "abort" | "skip"

@dataclass
class Job:
    id: str                        # unique, e.g. "refuel_t3_a1f9"
    task: Types.Task_Status        # what category this is
    steps: list[Step]              # ordered primitives to execute
    priority: int                  # higher = more urgent
    preemptable: bool = True       # can MCP interrupt this mid-job?
    on_complete: Callable | None   # callback to MCP when done
    on_abort: Callable | None      # callback if interrupted
```

The key is `preemptable`. A `REFUEL` job is not preemptable — once a turtle is heading home for fuel, you don't want the MCP to reroute it. A `MINE` job is preemptable — it's fine to interrupt tunneling.

---

## Per-Turtle Job Queue

Each turtle holds a small queue. The MCP can push to **front** (urgent preemption) or **back** (normal scheduling):

```python
class Turtle:
    job_queue: deque[Job]
    current_job: Job | None
    current_step_index: int

    def inject_urgent(self, job: Job):
        """MCP-called. Suspends current job, runs this first."""
        if self.current_job and not self.current_job.preemptable:
            return False  # MCP is told: not now
        if self.current_job:
            self.current_job.on_abort and self.current_job.on_abort()
        self.job_queue.appendleft(job)
        self.current_job = None
        return True

    def enqueue(self, job: Job):
        """MCP-called. Normal scheduling."""
        self.job_queue.append(job)

    def tick(self) -> Step | None:
        """Called each 0.25s tick. Returns next command to send."""
        if not self.current_job:
            if not self.job_queue:
                return None
            self.current_job = self.job_queue.popleft()
            self.current_step_index = 0

        step = self.current_job.steps[self.current_step_index]
        return step

    def report_step_result(self, success: bool, result: str):
        """Lua client calls back. MCP observes via callback."""
        step = self.current_job.steps[self.current_step_index]
        if not success:
            match step.on_fail:
                case "retry":   return          # don't advance index
                case "skip":    pass            # advance anyway
                case "abort":
                    self.current_job.on_abort and self.current_job.on_abort()
                    self.current_job = None
                    return
        self.current_step_index += 1
        if self.current_step_index >= len(self.current_job.steps):
            self.current_job.on_complete and self.current_job.on_complete()
            self.current_job = None
```

---

## MCP: Utility Scorer Feeds the Queue

The MCP runs a scoring loop. For idle turtles (empty queue), it scores and assigns. For active turtles, it monitors and decides whether to preempt:

```python
class Master_Control_Program:

    def score_turtle(self, turtle: Turtle) -> Types.Task_Status:
        scores = {
            Task_Status.REFUEL:          self._score_refuel(turtle),
            Task_Status.DEPOSIT:         self._score_deposit(turtle),
            Task_Status.MINE_FUEL:       self._score_mine_fuel(turtle),
            Task_Status.MINE_RESOURCES:  self._score_mine_resources(turtle),
            Task_Status.SMELT:           self._score_smelt(turtle),
            Task_Status.REPRODUCE:       self._score_reproduce(turtle),
        }
        return max(scores, key=scores.get)

    def _score_refuel(self, turtle: Turtle) -> float:
        deficit = max(0, turtle.refuel_threshold - turtle.fuel)
        return (deficit / turtle.refuel_threshold) * 100

    def _score_deposit(self, turtle: Turtle) -> float:
        return turtle.inventory_fullness() * 80

    def _score_mine_resources(self, turtle: Turtle) -> float:
        # Baseline desire to mine, reduced if swarm already has many miners
        active_miners = self._count_turtles_doing(Task_Status.MINE_RESOURCES)
        return max(0, 20 - (active_miners * 5))

    # --- Main orchestration loop ---

    async def orchestration_loop(self):
        while self.running:
            for turtle in self.turtles.values():
                # Always re-score, even active turtles
                best_task = self.score_turtle(turtle)
                urgency = self.get_score(turtle, best_task)

                if turtle.current_job is None and not turtle.job_queue:
                    # Turtle is idle — assign work
                    job = self.build_job(turtle, best_task)
                    turtle.enqueue(job)

                elif urgency > PREEMPT_THRESHOLD:
                    # Something urgent came up — try to interrupt
                    job = self.build_job(turtle, best_task)
                    job.priority = urgency
                    turtle.inject_urgent(job)   # may be refused if non-preemptable

            await asyncio.sleep(0.25)
```

`PREEMPT_THRESHOLD` is the key tuning knob. Setting it to 90 means only near-death fuel situations trigger a mid-job interrupt.

---

## Job Factory: Where MCP Puppeteers

`build_job` is where the MCP translates a task into a concrete sequence of Lua commands. This is the "puppet strings" layer:

```python
def build_job(self, turtle: Turtle, task: Task_Status) -> Job:
    match task:
        case Task_Status.REFUEL:
            return self._job_refuel(turtle)
        case Task_Status.DEPOSIT:
            return self._job_deposit(turtle)
        case Task_Status.MINE_RESOURCES:
            return self._job_mine_tunnel(turtle)
        # ...

def _job_refuel(self, turtle: Turtle) -> Job:
    path = self.pathfind(turtle.pos, self.fuel_depot)
    steps = [Step(cmd, expected="true", on_fail="retry") for cmd in path]
    steps.append(Step("turtle.refuel()", expected=None, on_fail="skip"))
    return Job(
        id=f"refuel_{turtle.gameID}_{uuid4().hex[:4]}",
        task=Task_Status.REFUEL,
        steps=steps,
        priority=100,
        preemptable=False,          # once heading for fuel, don't stop
        on_complete=lambda: self._on_refuel_complete(turtle)
    )
```

The MCP builds the **entire path as a step list** upfront. If the world changes mid-job (a block appears), `on_fail="retry"` handles it, and on repeated failure the job aborts and the MCP re-plans.

---

## Swarm-Level Control (the Manager Standpoint)

This is where the puppet model really pays off. The MCP can now issue **coordinated multi-turtle jobs** trivially:

```python
def coordinate_smelt_run(self):
    """MCP decides smelting is needed. Assigns roles to specific turtles."""
    carrier = self.find_best_turtle_for(Task_Status.DEPOSIT)
    smelter = self.find_best_turtle_for(Task_Status.SMELT)

    # Inject jobs in dependency order
    carrier_job = self._job_deposit_to_furnace(carrier)
    smelt_job   = self._job_smelt(smelter)

    # Smelt job waits for carrier to arrive
    smelt_job.on_start = lambda: self.wait_for_job(carrier_job.id)

    carrier.inject_urgent(carrier_job)
    smelter.inject_urgent(smelt_job)
```

Because all decisions live in MCP and turtles are just executors, coordinating across turtles requires no changes to turtle code — it's just the MCP building interdependent jobs.

---

## Summary of What Goes Where

| Concern | Lives In |
|---|---|
| "What should I do?" | MCP utility scorer |
| "When should I override my current task?" | MCP preemption logic + threshold |
| "What exact commands achieve this?" | MCP job factory |
| "Did that command succeed?" | Turtle (reports back) |
| "What do I do if it fails?" | Step's `on_fail` policy |
| "Am I done?" | Turtle (triggers `on_complete` callback to MCP) |

The turtle's only "intelligence" is: pull next step, send it, report result. Everything else is MCP's problem — which is exactly what gives you clean, testable orchestration logic without touching the Lua client.
