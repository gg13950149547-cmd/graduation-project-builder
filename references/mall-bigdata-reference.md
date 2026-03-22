# Mall Big Data Reference

This note captures the second source pattern used to strengthen the skill.

Source project:

- `D:\项目\基于大数据技术的郑州市大型商场数据统计分析`

## Product shape

- data pipeline with simulated raw data
- cleaning and analysis scripts
- HDFS upload path
- MySQL sync path
- Flask login and dashboard views
- report export and map screen

## Why this project matters

It represents a common graduation-project reality:

- the title and technical architecture sound heavy
- the actual implementation must be lighter and locally runnable
- the project still needs to preserve the module names and delivery story for defense

## Concrete pattern extracted from it

### 1. Keep the architecture narrative

The project still presents:

- data acquisition
- preprocessing
- storage
- analysis
- visualization

Even though the underlying implementation is simplified.

### 2. Replace hard dependencies with defendable simulations

The project uses:

- simulated local data instead of costly real data access
- local pipeline scripts instead of distributed production workflows
- a local Flask dashboard instead of a complex platform deployment
- optional Hadoop and database sync surfaces instead of mandatory full-cluster execution

This is a valid graduation-project strategy when cost, time, or environment blocks a full build.

### 3. Preserve the full delivery loop

The project still includes:

- quick-start documentation
- pipeline entrypoint
- dashboard startup scripts
- HDFS and MySQL sync commands
- report export output
- delivery bundle

This is the baseline for mixed data-project automation.

## Generalization rule

When a project has an ambitious title but limited implementation budget:

- keep the module names
- keep the architecture language
- simplify the data source
- simplify the heavy platform dependency
- keep the demo path real and reproducible

The goal is not to fake functionality. The goal is to preserve the intended system shape while implementing a smaller version that is runnable and explainable.
