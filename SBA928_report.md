# SBA 928 — Enhancing Market Research with AI Prompt Engineering

**Name:** Brittney Perry
**Course:** UCI 3025.0 — AI Prompt Engineering
**Date:** August 2026

---

## 1. Introduction and Objective

This assessment applies AI prompt engineering and model fine-tuning to a market research
problem. The work is divided into two phases, which are related but technically separate.
Prompt engineering changes the instructions sent to a model without modifying the model
itself. Fine-tuning trains the model on structured examples so that its parameters are
updated.

I used the UCI Bank Marketing dataset, which records the outcomes of a Portuguese bank's
direct marketing campaigns for term deposits. The goal was to determine whether a small
language model could be trained to produce useful market research analysis from customer
data, and to identify where that approach succeeds, where it fails, and what biases it
introduces.

All work was run locally on CPU using `google/flan-t5-small`.

---

## 2. Dataset

**Source:** UCI Machine Learning Repository — Bank Marketing (Moro, Rita & Cortez, 2014)
**URL:** https://archive.ics.uci.edu/dataset/222/bank+marketing
**License:** CC BY 4.0
**File used:** `bank-additional/bank-additional-full.csv`
**Size:** 41,188 rows × 21 columns
**Overall conversion rate:** 11.27%

I chose this dataset because it supports two of the required research areas from a single
source. It contains demographic and behavioral columns — age, job, education, marital
status, loan status, contact channel, and campaign history — which cover consumer behavior.
It also contains macroeconomic indicators recorded between May 2008 and November 2010:
`emp.var.rate`, `cons.price.idx`, `cons.conf.idx`, `euribor3m`, and `nr.employed`. That
period spans the financial crisis, which makes market trend analysis possible against real
economic movement.

I initially retrieved the dataset through the `ucimlrepo` package, which returned a
16-column version without the economic indicators. I switched to the 20-column
`bank-additional-full.csv` file because the indicator columns were required for the market
trends analysis.

### Limitation — competitor analysis

The assessment lists three market research areas: consumer behavior, market trends, and
competitor analysis. This dataset contains records from a single institution and holds no
data on competing banks, competitor pricing, or market share. I therefore could not perform
genuine competitor analysis, and I did not want to present internal channel comparisons as
though they were competitive intelligence.

I addressed this partially by including segment benchmarking, where each customer segment is
evaluated against the overall population rate. This is the same analytical operation as
competitive benchmarking, applied internally rather than across firms. A complete competitor
analysis would require a second data source such as industry-level term deposit rates or
market share reporting, which was outside the scope of a one-day assessment. I am recording
this as a known gap rather than overstating what the data supports.

---

## 3. Part 1 — Prompt Engineering

### 3.1 Strategy

I tested four prompt designs against the same source data, changing one dimension at a time:
the number of tasks requested, the framing of the question, the presence of a role
assignment, and the output constraint. Holding the data and the model constant meant any
difference in output could be attributed to the prompt itself.

### 3.2 Prompt Variations Tested

| ID | Design | Prompt |
|----|--------|--------|
| A | Multi-part numbered list | Analyze the following customer review… Identify: 1. strongest positive feature 2. primary problem 3. one recommendation |
| B | Single direct question | What is the main problem customers report with this product? |
| C | Single question, positive framing | What feature do customers like most about this product? |
| D | Role assignment + constraint | You are a market research analyst… In one sentence, state the product defect… |

Source data held constant across all four: a reusable water bottle rated 2 out of 5, with a
review stating the bottle keeps drinks cold but the lid leaked after two weeks.

### 3.3 Results

| ID | Output | Assessment |
|----|--------|------------|
| A | `1.` | Failed — produced only the list marker |
| B | `The lid is not working properly.` | Correct extraction from source data |
| C | `It's a great product.` | Contradicted the source (2/5 rating, reported defect) |
| D | Echoed the input prompt verbatim | Failed — no analysis produced |

Full output is in `part1_baseline_results.txt`.

### 3.4 Analysis

Variation A asked for three things at once: the positive feature, the problem, and a
recommendation. The model returned only "1." — the first character of the format I asked
for, and nothing else. FLAN-T5-small has 77 million parameters, which is not enough to hold
three separate tasks in one response. The takeaway is that with a small model you have to
break the task up yourself in the prompt instead of expecting the model to manage it.

Variation B asked one direct question and got a correct answer: "The lid is not working
properly." Same data, same model, but a single objective instead of three.

Variation C is the result that matters most. I asked what customers liked most about a
product rated 2 out of 5 with a broken lid, and the model said "It's a great product." Two
stars does not describe a great product. The model answered the framing of my question
instead of reading the data. For market research that is a real problem — if an analyst
writes prompts around what they already believe, the model will hand back agreement, and it
will look like a finding. The bias comes from how the prompt is written, not from the data,
so it is easy to miss.

Variation D added a role ("You are a market research analyst") plus a one-sentence
constraint. I expected this to help since role prompting is standard advice. It made things
worse — the model repeated my input back instead of analyzing it. My read is that role
prompting works on large models and does not transfer down to small ones, where the extra
wording just competes with the actual task. It shows that prompt techniques need to be
tested on the model you are actually using rather than assumed.

Based on these results I carried the direct, single-objective structure forward into the
fine-tuning phase, and avoided role preambles.

---

## 4. Part 2 — Fine-Tuning

### 4.1 Training Data Construction

Each record contains three fields, as specified:

- `instruction` — the task
- `context` — facts drawn from the source dataset
- `target` — the expected response

Five record types were generated, all grounded in statistics computed from the source data:

1. **Customer profile analysis** — 180 records sampled from source rows
2. **Occupational segment benchmarks** — one per job category
3. **Economic indicator interpretation** — one per macroeconomic variable
4. **Campaign fatigue assessment** — one per contact count, 1 through 8
5. **Monthly seasonality** — one per month present in the data

Instruction phrasing was varied across records within each type so the model would not
overfit to a single wording.

**Splits:** 70% train / 15% validation / 15% held-out evaluation, assigned after shuffling.
No record appears in more than one split. The held-out set was used only after training was
complete.

| Split | Records |
|---|---|
| Train | 149 |
| Validation | 32 |
| Held-out evaluation | 33 |
| **Total** | **214** |

### 4.2 Accuracy Review — Defect Found and Corrected

Before training, I reviewed the generated records to check that each expected response was
actually supported by its context. This review found a logical inconsistency in the customer
profile records.

Some records rated a customer as "Low" conversion likelihood while citing a benchmark that
was above average. One example classified an admin. customer as Low, then stated that the
admin. segment converts at 13.0% against an overall rate of 11.3%. A 13.0% rate is better
than average, so the record contradicted its own conclusion.

The cause was in how I built the target text. The likelihood rating averaged five signals —
occupation, education, age cohort, prior campaign outcome, and contact timing — but the
sentence explaining that rating only ever reported the occupation rate. When occupation was
the one strong signal and the other four were weak, the text presented favorable evidence
next to an unfavorable verdict.

I corrected the generation logic to report both the strongest and the weakest signal instead
of occupation alone. The same record now reads: "Conversion likelihood: Moderate. Strongest
signal: education level at 13.7%. Weakest signal: prior campaign outcome at 8.8%, against a
11.3% overall benchmark." The verdict is now visibly consistent with the evidence given.

Training on the original records would have taught the model to produce self-contradicting
analysis. This is why the accuracy review matters before training rather than after — the
defect was in the training signal itself, and no amount of evaluation afterward would have
separated it from normal model error.

### 4.3 Training Configuration

| Parameter | Value |
|---|---|
| Base model | `google/flan-t5-small` |
| Learning rate | 3e-4 |
| Batch size | 4 (train and eval) |
| Epochs | 5 |
| Max input length | 256 tokens |
| Max target length | 160 tokens |
| Device | CPU |
| Total steps | 190 |
| Training runtime | 96.1 seconds |
| Final training loss | 0.5686 |
| Checkpoint | `./flan-market-research-final` |

**Preprocessing:** instruction and context were concatenated as
`{instruction}\nContext: {context}` and tokenized with the T5 tokenizer. Targets were
tokenized separately as labels. Padding was applied dynamically via
`DataCollatorForSeq2Seq`.

**Adjustment made during setup:** the initial environment installed `transformers` 5.14.1,
which removed the `text2text-generation` pipeline task and caused a `KeyError` on load. I
pinned the library to `transformers<5`, which installed 4.57.6 and resolved it.

### 4.4 Validation Loss

| Epoch | Validation loss |
|---|---|
| 3 | 0.3139 |
| 4 | 0.2783 |
| 5 | 0.2676 |

Validation loss decreased at every epoch and did not diverge from training loss, so there is
no evidence of overfitting at 5 epochs. Loss was still falling at the final epoch, which
suggests the model had not saturated and additional epochs may have improved it further.

---

## 5. Base vs Fine-Tuned Comparison

Both models were evaluated on held-out records using identical generation settings
(`max_new_tokens=160`, `do_sample=False`). Full output is in `comparison.txt`.

### 5.1 Example

**Context:** Age 46 (46–55), technician, university degree, married, housing loan yes,
cellular, August, **14 contacts this campaign**, prior outcome nonexistent, Euribor 3m 4.962.

| | Output |
|---|---|
| **Base** | `Euribor 3m is 4.962.` |
| **Fine-tuned** | `Conversion likelihood: Low. Strongest signal: education level at 13.7%. Weakest signal: age cohort at 8.7%, against a 11.3% overall benchmark. Primary barrier: below-average response for this age cohort. Recommendation: deprioritize; retarget after 90 days with a lower-minimum product.` |
| **Reference** | `Conversion likelihood: Moderate. … Primary barrier: repeated contact fatigue (14 contacts this campaign). Recommendation: include in standard outreach with a tailored rate offer.` |

### 5.2 Assessment Against Required Dimensions

The base model produced "Euribor 3m is 4.962." It pulled one number out of the context and
stopped. It did not give a likelihood, a barrier, or a recommendation. The fine-tuned model
returned the full four-part structure and reported the statistics correctly — education at
13.7%, age cohort at 8.7%, and the 11.3% benchmark all matched the reference. The biggest
difference is that the fine-tuned model learned the format and learned to pull the right
numbers, while the base model did neither.

| Dimension | Finding |
|---|---|
| Relevance | Fine-tuned output addressed the question asked; base output did not |
| Specificity | Fine-tuned cited three specific rates; base cited one unrelated figure |
| Factual consistency | All statistics in the fine-tuned output matched the reference — the model retrieved real values rather than inventing them |
| Completeness | Fine-tuned produced all four required components; base produced none |
| Format adherence | Fine-tuned reproduced the structure exactly; base had no structure |
| Usefulness for market research | Fine-tuned output is directly actionable; base output is not |
| Potential bias | Recommendations systematically deprioritize low-converting segments — see Section 6 |

### 5.3 Where Fine-Tuning Did Not Help

The model had two possible barrier rules available: contact fatigue, and below-average
response for the weakest signal. It saw the second one far more often. Out of 180 profile
records, 34 used the fatigue rule and 146 used the weak-signal rule, so after the 70%
training split the model saw the fatigue rule roughly 24 times. When it hit a record with 14
contacts, it defaulted to the pattern it had seen most, even though the contact count was in
the context in front of it. Fine-tuning taught it the common pattern more strongly than the
conditional rule.

It also misclassified the likelihood, returning Low where the reference was Moderate. Both
errors point the same direction: the model learned what an answer looks like more readily
than it learned when a rule applies.

**This is a consistent failure, not an isolated error.** Five of the eight held-out
evaluation records contained a contact count of 4 or higher, which is the threshold at which
the fatigue rule applies. The fine-tuned model failed to apply the rule in all five:

| Evaluation | Contacts | Fatigue barrier identified |
|---|---|---|
| 2 | 6 | No |
| 3 | 14 | No |
| 4 | 4 | No |
| 7 | 6 | No |
| 8 | 4 | No |

The model applied the fatigue rule correctly in **0 out of 5** applicable cases, including
one with 14 contacts — more than three times the threshold. The rule was present in 18.9% of
the training data and the model did not learn it at all. This is the clearest result in the
evaluation: fine-tuning on an imbalanced set did not produce a weaker version of the minority
rule, it produced no version of it. The model reproduced the majority pattern every time.

---

## 6. Bias Analysis

### 6.1 Bias in Prompt Engineering

Variation C in Section 3 demonstrated leading-question bias directly. A positively framed
prompt produced a positive conclusion from source data that was negative. The model followed
the framing of the question rather than the evidence. In a market research context this means
prompt wording alone can manufacture a finding, and because the output looks like ordinary
analysis, there is nothing in the result that signals the problem.

### 6.2 Bias in the Training Dataset

**Demographic representation.** The 180 profile records were sampled randomly from 41,188
rows, which preserved the source distribution and its imbalances. `marital: unknown`
represents 0.19% of the source data and appears in **0 training records** — the category was
eliminated entirely by random sampling. The model has never seen that value.

**Small-sample distortion.** The `illiterate` education category has 18 rows in a dataset of
41,188. Its 22.22% conversion rate represents 4 conversions. That is not enough to support a
claim, but it still ranks above `university.degree`, which has 12,168 rows behind its number.
The same pattern appears in marital status, where `unknown` (80 rows) ranks highest at 15.0%.
Ranking segments by conversion rate alone puts the least reliable numbers at the top of the
list, where they look like the strongest findings.

**Bias in expected responses.** The targets encode a rule that recommends deprioritizing
segments with below-average conversion. Conversion rate varies by 24.54 points across
occupations, from blue-collar at 6.89% to student at 31.43%. The model therefore learns to
systematically deprioritize blue-collar customers and those with lower education levels.
This is an automated system directing access to a financial product away from lower-income
demographics, on the basis of historical response rates that may themselves reflect how
those groups were previously marketed to.

**Rule coverage.** 18.9% of profile records used the contact fatigue barrier and 81.1% used
the weak-signal barrier. As shown in Section 5.3, the model then failed to apply the fatigue
rule in 0 out of 5 applicable held-out cases. A condition present in roughly one fifth of the
training data was not learned at all.

This is the most important result for the fairness question, because it is measurable. The
same mechanism applies to demographic categories, not only to rules: `marital: unknown` has 0
training records and `education: illiterate` has 18 source rows. If a rule at 18.9%
representation is learned zero percent of the time, categories at 0.19% and 0.04% cannot be
expected to be handled correctly either. The difference is that the rule failure was
detectable because I had a reference to compare against — demographic failures of the same
kind would be invisible in aggregate metrics.

### 6.3 What the Data Does Not Record

This dataset records age, job, marital status, and education. It does not record race,
ethnicity, income, or region. That means the fairness analysis I can perform is limited to
the attributes the data happens to contain, and I cannot check whether the model's
recommendations fall unevenly across groups the dataset never recorded. Absence of a field is
not evidence of absence of bias.

### 6.4 Regional and Temporal Limitations

The data comes from a single Portuguese banking institution between May 2008 and November
2010. There is no regional variation within the sample, no basis for generalizing to other
countries or markets, and no coverage of product categories beyond term deposits. The period
also coincides with the financial crisis, and Section 4 established that conversions
concentrate in periods of falling rates and contracting employment. Patterns learned from
this window may not hold under normal economic conditions.

### 6.5 Data Validity — `duration` Leakage

The `duration` column records call length, which is only known after a call has completed.
Using it to predict whether a call will convert is circular. I excluded it from all context
fields and from the analysis for this reason.

---

## 7. Fairness Strategies

Each recommendation below responds to a specific issue identified in Section 6.

**1. Stratified sampling with a category floor.**
*Issue:* random sampling eliminated `marital: unknown` entirely and left rare categories
barely represented.
*Mitigation:* sample with a guaranteed minimum per category rather than proportionally.
*Verification:* confirm every source category appears in the training split before training.

**2. Minimum sample threshold for segment claims.**
*Issue:* `education: illiterate` (n=18) and `marital: unknown` (n=80) rank as top-performing
segments on point estimates alone.
*Mitigation:* require n ≥ 100 or report confidence intervals before a segment rate informs a
recommendation.
*Verification:* apply the threshold retroactively — it would have excluded both categories
above.

**3. Oversampling rare conditional branches.**
*Issue:* the contact fatigue rule appeared in only 18.9% of records and the model applied it
in 0 of 5 applicable evaluation cases.
*Mitigation:* deliberately balance conditional branches in training data rather than letting
sampling determine their frequency.
*Verification:* re-run the five fatigue evaluation cases and check whether the barrier is
correctly identified.

**4. Neutral prompt wording.**
*Issue:* positively framed prompts produced positive conclusions from negative data.
*Mitigation:* phrase prompts without directional framing, and test each prompt in both
positive and negative form.
*Verification:* compare outputs across framings on the same source record; substantive
disagreement indicates framing bias.

**5. Per-segment evaluation rather than aggregate metrics.**
*Issue:* aggregate validation loss fell every epoch and showed no sign of the total failure
on the fatigue rule.
*Mitigation:* report accuracy broken out by demographic segment and by rule branch.
*Verification:* a model with acceptable aggregate loss but uneven per-segment accuracy fails
this check where it would pass the aggregate one.

**6. Human review before recommendations affecting product access.**
*Issue:* the model's recommendations systematically deprioritize lower-income occupational
segments.
*Mitigation:* require human sign-off on any automated recommendation that determines who is
offered a financial product.
*Verification:* audit the distribution of "deprioritize" recommendations across demographic
groups on a recurring basis.

**7. Document scope as a stated limitation.**
*Issue:* the dataset covers one institution, one country, one product, one economic period,
and omits race, income, and region.
*Mitigation:* state this scope wherever the model's outputs are reported.
*Verification:* no conclusion should be presented without the accompanying scope statement.

---

## 8. Conclusion

Fine-tuning worked partly. It clearly worked on format and on retrieving the right numbers —
the model went from returning a single fact to producing complete, correctly-sourced
analysis. It did not work on conditional reasoning. The model failed to apply the contact
fatigue rule in all five held-out cases where it applied, including one customer contacted 14
times. Fine-tuning taught the model what an answer should look like more effectively than it
taught the model when a rule applies.

The gap between those two results is the finding I would carry forward. A model that produces
correctly formatted, correctly sourced, confidently worded analysis while silently ignoring a
rule it was trained on is harder to catch than one that fails obviously. The base model's
output was visibly useless. The fine-tuned model's output was wrong in a way that looks
right.

The prompt engineering phase produced the more transferable finding. Variation C showed that
a positively framed question can produce a positive conclusion from negative data, and that
failure mode does not depend on model size — it would occur on a large model as readily as on
this one.

With more time I would rebalance the training data so rare rules appear more often, apply
stratified sampling so no category is lost, and test whether that closes the reasoning gap. I
would also add a second data source to support genuine competitor analysis.

A 77-million-parameter model trained on 149 records is not a production system, and I am not
presenting it as one. The value of this work is in demonstrating the full pipeline — prompt
design, dataset construction, accuracy review, training, held-out evaluation, and bias
analysis — and in identifying specifically where and why it breaks.

---

## Appendix — Files Submitted

| File | Contents |
|---|---|
| `bank-additional/bank-additional-full.csv` | Source dataset |
| `flan_inference.py` | Base model inference check |
| `prompt_variations.py` | Part 1 prompt engineering script |
| `part1_baseline_results.txt` | Prompt variation outputs |
| `explore.py` / `stats.txt` | Dataset statistics |
| `build_dataset.py` | Training data generation |
| `train.jsonl` / `validation.jsonl` / `eval_holdout.jsonl` | Three-way split (149 / 32 / 33) |
| `review.py` | Record review utility |
| `train_flan.py` | Fine-tuning script |
| `flan-market-research-final/` | Saved model checkpoint |
| `compare_models.py` / `comparison.txt` | Base vs fine-tuned comparison |
| `bias_analysis.py` / `bias_results.txt` | Bias and representation analysis |

**Citation:** Moro, S., Rita, P., & Cortez, P. (2014). *Bank Marketing* [Dataset].
UCI Machine Learning Repository. https://doi.org/10.24432/C5K306
