# Development approach

This project follows the **Solve it with code** method, combining George Pólya's
*How to Solve It* (1945) with Jeremy Howard's adaptation for the language model era.

## The four steps

### 1. Understand the problem
State the problem precisely before writing anything. Identify:
- What do we know?
- What are we missing?
- What would a correct solution look like?

Do not move to step 2 until the problem is clearly stated. Vague problems produce
vague solutions.

### 2. Devise a plan
Break the problem into the smallest concrete steps that can each be verified
independently. Write the plan down. A step is small enough when you can describe
its expected output before running it.

### 3. Carry out the plan — incrementally
Write the simplest possible code that makes the next thing visible. Run it.
Look at the actual output. Then write the next piece.

**Code is a thinking tool, not just a deliverable.** The goal at each step is
to learn something, not to produce finished code. Finished code is the
by-product of enough small steps.

Rules:
- One step at a time
- Verify output before moving on
- If the output is surprising, stop and understand why before continuing
- Never design more than one step ahead of what has been verified

### 4. Review
Once a step works, look back:
- Does this actually solve the problem as stated?
- Is there anything simpler that would also work?
- What does this generalise to?

## How this shapes human–AI collaboration

- The **human drives** — writes the first attempt, decides what to tackle next
- The **AI assists** — helps unstick specific problems, suggests alternatives, spots errors
- The AI does not implement entire modules and hand them over for passive review
- Design discussions happen at the start of each step, not as a big upfront phase
- When the AI writes code, it writes the minimum needed to make the next thing visible

## In practice

Before writing any code, answer:
> *What is the one thing I want to be able to see or verify after this step?*

If you cannot answer that, the step is too large. Split it.
