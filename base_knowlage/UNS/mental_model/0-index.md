# The Expert's Mental Model: UNS Namespace Design

When an expert stares at a device datasheet with 200+ parameters, they're not just sorting data — they're building a **semantic layer** that will survive the next 10 years of operational evolution.

## The Expert's Inner Voice

> "I'm not organizing files. 
> I'm building a semantic API that will outlive me.
> Every placement is a promise about what this data means,
> who needs it, and why it exists.
> When I'm wrong, 47 dashboards break.
> When I'm right, the system explains itself."
>> That's the mental model. **Intentional semantics over convenient shortcuts.**

Here's the internal dialogue:

01. The Decision Tree (What's Actually Happening In Their Head)
    - **First Pass**: The Nature Question `What IS this data fundamentally?`
    - **Second Pass**: The Consumer Question `Who/what needs this data, and why?- `
    - **Third Pass**: The Lifecycle Question `When/why does this value change?`

02. The Expert's Checklist (For Every Single Parameter)
    - **Mutability Test** `Does this EVER change during operation?`
    - **Directionality Test** `Is this data flowing IN or OUT or ABOUT the device?`
    - **Calculation Test** `Is this measured or calculated?`
    - **The Action Test** `What happens if this value is wrong or missing?`

03. The Real Expert Thinking: Edge Cases
    - Case 1: Alarm Acknowledgement
    - Case 2: Setpoint Echo
    - Case 3: Error Codes
    - Case 4: Timestamps

04. The Mental Model: "Perspectives"
    - Operator Perspective `What do I need on my HMI right now?`
    - Maintenance Perspective `What tells me when/why to service?`
    - Analytics Perspective `What do I trend and analyze?`
    - Configuration Perspective `What can I tune?`

05. The Gotchas Experts Watch For
    - 1. **Overloading `status/`**
    - 2. **The Alarm State Explosion**
    - 3. **The Config vs. Asset Boundary**
    - 4. **The Timestamp Trap**

06. The Real Expert Move: Namespace Documentation
    - They ALWAYS populate `meta/`

07. The Final Expert Test Before committing, they ask:
    - **"Can I explain this to a new hire in 30 seconds?"**
    - **"Will this break if we add 50 more devices?"**
    - **"Can I write one Spark/SQL query to get all measurements across all devices?"**
    - **"If this value is missing, which dashboard breaks?"**

---