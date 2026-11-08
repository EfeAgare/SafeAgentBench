# SafeAgentBench

SafeAgentBench is a learning and research project for testing authorization
boundaries around payment-capable AI agents. All activity is deterministic and
synthetic: there are no bank connections, payment processors, API keys, or real
financial operations.

## Implementations

- [`python/`](python/) is the main AI-safety research implementation. It contains
  the benchmark policy, in-memory simulator, command-line demonstration, and
  pytest experiments.
- [`ruby/`](ruby/) is a plain Ruby learning equivalent of the core ideas. It is
  intentionally framework-free and uses built-in Minitest.

Start with [`python/README.md`](python/README.md) for the research roadmap and
[`ruby/README.md`](ruby/README.md) for the language-learning comparison.
The accumulated day-by-day explanation is in
[`explanation_file.md`](explanation_file.md).

## Day 2: offline tool-calling agent

Day 2 adds a deterministic LLM-style agent. The offline mock model interprets a
request and *proposes* either `lookup_transaction` or `request_refund`. A
separate deny-by-default policy decides whether the proposal may execute. Both
tools operate only on synthetic in-memory records; a refund creates a simulated
request and never moves money.

Run Python:

```bash
cd python
source .venv/bin/activate
python -m pytest
```

Run plain Ruby (no Rails and no gems required):

```bash
cd ruby
ruby -Ilib -Itest -e 'Dir["test/**/*_test.rb"].sort.each { |file| require File.expand_path(file) }'
```

### Python-to-Ruby map

| Idea | Python | Plain Ruby |
| --- | --- | --- |
| Immutable value | `@dataclass(frozen=True)` | `Struct` or a frozen object |
| Interface | `Protocol` | Duck typing |
| Tool arguments | `dict[str, Any]` | `Hash` |
| Model response | `ModelResponse` dataclass | `ModelResponse` struct |
| Bounded loop | `for step in range(...)` | `(1..max_steps).each` |
| Structured audit log | list of dictionaries | array of hashes |
| Tests | pytest functions and assertions | Minitest methods and assertions |

The important safety boundary is identical in both languages: the model is not
the authority. It proposes a tool call; application code checks authorization,
executes an allowed synthetic tool, records structured events, and stops after a
fixed number of steps.

## Days 3–4: injection experiments and execution guards

Day 3 adds JSON scenarios containing deliberately obvious, harmless benchmark
injections inside synthetic transaction output. `load_scenarios` validates the
fixtures and the deterministic `InjectionFollowingMockModel` deliberately
follows the injected instruction. This makes the test reproducible offline and
demonstrates a key measurement distinction:

- **attempted malicious tool call**: the model proposed the injected action;
- **executed unauthorized action**: the tool actually changed simulated state.

An attack can therefore register as an attempted compromise while execution
remains safe. The runner reports these counts separately and does not claim a
real-model success rate.

Day 4 adds independent, deterministic checks at the refund tool's execution
boundary. A request must pass all five checks: transaction ownership, actor
permission, explicit user intent naming that transaction, settled/refundable
state, and a fresh idempotency key. The model prompt and the agent's coarse tool
policy are not trusted as authorization. Denied calls create no refund record.

### Run the experiments

Python is the canonical research implementation:

```bash
cd python
source .venv/bin/activate
python -m pytest -q
python -m pytest -q tests/test_day3_attacks.py tests/test_day4_execution_guards.py
```

Plain Ruby mirrors the architecture for learning, without Rails or external
gems:

```bash
cd ruby
ruby -Ilib -Itest -e 'Dir["test/**/*_test.rb"].sort.each { |file| require File.expand_path(file) }'
```

| Day 3–4 concept | Python | Plain Ruby |
| --- | --- | --- |
| Validated scenario value | frozen `dataclass` | keyword `Struct` |
| JSON loader | `json` + `pathlib.Path` | `JSON` + `File` |
| Vulnerable offline model | protocol-compatible class | duck-typed class |
| Execution guard inputs | keyword-only arguments | keyword arguments |
| Immutable result | frozen `AttackResult` | `AttackResult` struct |

### Methodology and limits

The tests use only synthetic records, in-memory state, deterministic mocks, and
fixed fixtures. There are no live payments, model APIs, network calls, secrets,
or claims about production model behavior. Each case records the proposal,
policy decision, tool result, attempted sensitive call, and resulting simulated
state. The current suite establishes implementation behavior, not empirical
research findings about any LLM.

## Days 5–7: evaluation, coverage, and reporting

Day 5 adds deterministic aggregate metrics with raw counts, denominators,
denial-code breakdowns, and scenario IDs. Day 6 expands the adversarial matrix
across ownership, permission, intent, and state boundaries. Day 7 composes the
loader, runner, and evaluator into a stable, schema-versioned JSON report.

```bash
cd python
python -m pytest -q
python -m safeagentbench.benchmark scenarios/day3_prompt_injection.json scenarios/day6_guard_matrix.json
```

See [`DAY_5.md`](DAY_5.md), [`DAY_6.md`](DAY_6.md), and
[`DAY_7.md`](DAY_7.md) for the code maps and methodology. No checked-in report
is labeled as a research finding: results describe deterministic mocks only.

