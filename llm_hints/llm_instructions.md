@llm_hints/llm_instructions.md
@llm_hints/sources/paper_cond_coop.md
@llm_hints/superpowers/plans/2026-06-04-coop-disaster-sim.md
@llm_hints/superpowers/specs/2026-06-04-coop-disaster-sim-design.md


# LLM Instructions

## Source material
The context for this project is [the paper](sources/paper_cond_coop.md). Scan it for relevant information to understand the codebase and the purpose of the project. 

## Runtime Management
### Python Runtime
- use system wide uv to manage python virtual environment .venv

## Documentation
- Use consise but meaningful comments. The goal is to minimize cognitive load when reading the code, while still providing enough information to understand the purpose and functionality of each part of the code.
- Use docstrings for functions and classes to explain their purpose, parameters, and return values.
- Remember to update the markdown documentation in the repository to reflect any changes made to the codebase

## Formatting
- Always use black for code formatting to ensure consistency across the codebase. 

## Make no mistakes
Make no mistakes