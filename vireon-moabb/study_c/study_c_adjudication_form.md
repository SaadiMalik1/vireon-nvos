# Study C Adjudication Form — Experiment C-__

**Adjudicator:** [name]
**Date:** [date]
**Experiment ID:** C-__
**VIREON version:** frozen at commit [hash]

---

## Experiment Information

**Paper:** [citation]
**Dataset:** [name]
**Pipeline:** [description]
**Evaluation:** [strategy]

---

## Reproduction Results

**Published accuracy:** [value]%
**Reproduced accuracy:** [value]%
**Difference:** [value]%
**Reproduction status:** [Success / Failure / N/A]

---

## VIREON Validation Profile

### Correctness
- Mean accuracy: [value]
- Chance level: [value]
- Above chance: [PASS / FAIL]

### Methodological validity
- Partition integrity: [PASS / FAIL — details]
- Subject isolation: [PASS / FAIL — details]
- Session isolation: [PASS / FAIL — details]

### Statistical validity
- Subject-level CI: [[lower, upper]]
- Permutation p-value: [value]
- Statistical unit: [PASS / FAIL — details]

### Robustness
- Channel dropout (20%): [drop value] — [PASS / WARNING]
- White noise (10%): [drop value] — [PASS / WARNING]
- Line noise (50Hz): [drop value] — [PASS / WARNING]

### Reproducibility
- Seed recorded: [PASS / FAIL]
- Environment captured: [PASS / FAIL]
- Timestamps recorded: [PASS / FAIL]

### Evidence integrity
- Hash: [value]
- Verify: [PASS / FAIL]

---

## VIREON Findings

### Finding F-1: [title]

**What VIREON detected:** [description]

**VIREON classification:** [V0 / V1 / V2]

**Relevant evidence:**
- [evidence item 1]
- [evidence item 2]

**Evidence bundle hash:** [value]

---

### Finding F-2: [title] (if applicable)

**What VIREON detected:** [description]

**VIREON classification:** [V0 / V1 / V2]

**Relevant evidence:**
- [evidence items]

---

## Adjudicator Questions

For each finding (F-1, F-2, ...):

### Finding F-N

**1. Is the finding technically reproducible?**
- [ ] Yes
- [ ] No
- [ ] Insufficient evidence

**2. Is the finding scientifically meaningful?**
- [ ] Yes
- [ ] No
- [ ] Insufficient evidence

**3. Is it a genuine methodological concern?**
- [ ] Yes
- [ ] No
- [ ] Insufficient evidence

**4. Is the evidence sufficient to support the finding?**
- [ ] Yes
- [ ] No
- [ ] Insufficient evidence

**5. What is the severity?**
- [ ] Critical (invalidates the result)
- [ ] Major (affects interpretation)
- [ ] Minor (worth noting)
- [ ] Not a concern

**6. Would the issue affect interpretation of the original result?**
- [ ] Yes
- [ ] No
- [ ] Uncertain

**ADJUDICATOR VERDICT:**
- [ ] Confirmed (genuine methodological issue → V3)
- [ ] Partially confirmed (issue exists but limited impact)
- [ ] Not confirmed (not a genuine concern)
- [ ] Insufficient evidence (cannot adjudicate)

**ADJUDICATOR COMMENTS:**
[free text — explain reasoning, note any additional issues VIREON missed, suggest improvements]

---

## Additional Issues (not found by VIREON)

Did the adjudicator identify methodological concerns that VIREON did NOT flag?

- [ ] No additional issues
- [ ] Yes (describe below):

[description of issues VIREON missed]

---

## Overall Assessment

**VIREON classification:** [V0 / V1 / V2]

**Adjudicator final classification:**
- [ ] V0 — No additional concern (VIREON correct)
- [ ] V1 — Additional characterization (VIREON correct)
- [ ] V2 → V3 — Confirmed methodological concern
- [ ] V2 → Not confirmed — False positive
- [ ] V2 → Insufficient evidence

**Adjudicator confidence:** [High / Medium / Low]

**Time to adjudicate:** [minutes]

---

## Adjudicator Signature

Name: _________________
Date: _________________
Signature: _________________
