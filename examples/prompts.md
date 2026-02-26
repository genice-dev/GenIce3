# Example prompts for GenIce3

These are example prompts for **someone who does not know GenIce3** to ask an AI (e.g. Gemini, ChatGPT) and get a working command, script, or config. The AI must use the GenIce3 manual to answer correctly.

## How to get good answers

**The AI needs the manual.** Many AIs do not reliably open URLs you paste. So:

1. **Option A (recommended):** Open the **“For AI assistants”** page in your browser, copy the whole page text, and paste it into the AI chat *before* your question. Then ask one of the prompts below.  
   - Page: **https://genice-dev.github.io/GenIce3/for-ai-assistants/**  
   - That page is a short summary of GenIce3 written for AIs (unit cells, CLI, API, options).

2. **Option B:** Send the AI the link and ask it to read the manual, then ask your question.  
   - Manual: **https://genice-dev.github.io/GenIce3**  
   - Repository (docs in `docs/`): **https://github.com/genice-dev/GenIce3**

3. **Option C:** If you use an IDE (e.g. Cursor) with the GenIce3 repo open, you can point the AI at the `docs/` folder so it reads the files directly.

---

## Example prompts

Copy one of these and send it to the AI (after giving it the manual as above, if needed).

### CLI (sI hydrate, GROMACS, TIP4P)

- **GenIce3** is a program that generates ice and clathrate structures. Its manual is at https://genice-dev.github.io/GenIce3 (repository: https://github.com/genice-dev/GenIce3). Using that manual (or the “For AI assistants” page), write a **GenIce3 CLI command** that: generates an sI clathrate hydrate 2×2×2 with United-atom methane in all cages, GROMACS format, and TIP4P water.

### API (zeolite, GROMACS, TIP4P)

- **GenIce3** is a Python library for generating ice structures. Manual: https://genice-dev.github.io/GenIce3 (or the “For AI assistants” page). Using that manual, write **Python code** that uses the GenIce3 API to: generate a zeolite LTA ice structure 2×2×2, GROMACS format, TIP4P water. (Zeolite uses the `zeolite` unit cell with a 3-letter IZA code such as LTA or FAU; see the Unit cells page in the manual.)

### Config file / YAML (aeroice, GROMACS, TIP5P)

- **GenIce3** can be driven by a YAML config file. Manual: https://genice-dev.github.io/GenIce3 (or the “For AI assistants” page). Using that manual, write a **GenIce3 config file (YAML)** that: generates an aeroice structure with prism length 3, GROMACS format, TIP5P water. (The aeroice unit cell takes a `length` option; see the Unit cells page in the manual.)
