# DyJ Performance AI

An AI-powered **ChatGPT plugin** developed for **Club Social y Deportivo Defensa y Justicia** to help performance and medical staff analyze player injury and workload data.

## What it does

Performance AI allows staff to ask questions about club data in natural language, such as:

- Which players have recurring muscle injuries?
- Are there patterns before certain injuries?
- Which players suffered a recurrence shortly after returning to play?
- Are recent match loads associated with particular injury patterns?

The plugin includes two AI skills:

- **Visual Skill:** presents data through clear charts, tables and performance indicators.
- **Context Skill:** explains findings in simple, concise and contextualized language.

The goal is to turn historical performance data into useful insights without requiring staff to manually analyze spreadsheets.

## How it works

1. Performance staff upload and manage Excel files through a **Streamlit app**.
2. The **ChatGPT plugin** connects to the data using **Model Context Protocol (MCP)**.
3. ChatGPT retrieves and analyzes the relevant information.
4. The two skills help present and explain the findings clearly.

## Demo data

The dataset included in this repository is **100% synthetic**.

Player names, injuries, workloads and medical events are fictional and were created exclusively to test the prototype. **No real medical or performance data from Defensa y Justicia is included.**

## Disclaimer

Performance AI is designed as a decision-support tool. It does not provide medical diagnoses or replace the judgment of qualified medical and performance professionals.

## Status

🚧 Early-stage academic prototype / MVP.
