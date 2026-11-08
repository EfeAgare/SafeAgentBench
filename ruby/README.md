# SafeAgentBench — Ruby learning implementation

This is a small, dependency-free Ruby translation of the benchmark's core
authorization and synthetic-payment ideas. It uses plain Ruby objects rather
than Rails, Active Record, a database, controllers, or network services.

The `python/` implementation remains the main AI-safety research benchmark.
This folder is a learning companion for comparing language idioms.

## Run the tests

Ruby 2.6 or newer is sufficient. Minitest and Rake ship with standard Ruby
installations, so no bundle install or database setup is required.

```bash
cd ruby
ruby -Ilib -Itest -e 'Dir["test/**/*_test.rb"].sort.each { |file| require File.expand_path(file) }'
```

If Rake is available, `rake test` runs the same suite.

## Layout

- `lib/safe_agent_bench/models.rb` — immutable request, authorization, decision,
  and ledger values.
- `lib/safe_agent_bench/authorization_policy.rb` — pure deny-by-default checks.
- `lib/safe_agent_bench/payment_simulator.rb` — in-memory synthetic execution
  boundary with replay protection.
- `test/` — focused Minitest examples corresponding to the Python tests.

No real payment is ever initiated.

