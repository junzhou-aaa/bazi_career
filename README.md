# Bazi Career Planning CLI 🔮💼

Welcome to the **Bazi Career Planning CLI**! This unique tool combines traditional Chinese metaphysics (Four Pillars of Destiny / BaZi) with modern Artificial Intelligence (LLMs) to provide deeply personalized career planning, job matching, and historical life validation.

Whether you're looking for your next big career move or trying to understand if your upcoming "Luck Cycles" favor taking a risk, this tool helps you map it out.

---

## 🛠️ Installation Guide (For Beginners)

Even if you have no programming experience, just follow these steps to get the tool running on your Mac or PC!

### Prerequisites
- **Python 3.10 or higher**: Make sure Python is installed. (Check by typing `python3 --version` in your terminal).
- **An API Key**: You will need an API Key from OpenAI, Anthropic (Claude), or DeepSeek.

### Step-by-Step Setup

**1. Clone the project**
Open your terminal and download the project to your computer:
```bash
git clone https://github.com/junzhou-aaa/bazi_career.git
cd bazi_career
```

**2. Create a Virtual Environment**
This keeps everything clean and isolated on your computer:
```bash
python3 -m venv venv
```

**3. Activate the Environment**
- On **Mac/Linux (Bash/Zsh)**: 
  ```bash
  source venv/bin/activate
  ```
- On **Mac/Linux (Fish Shell)**: 
  ```bash
  source venv/bin/activate.fish
  ```
- On **Windows**: 
  ```bash
  venv\Scripts\activate
  ```

**4. Install the CLI Tool**
Install the tool so you can use the `bazi-career` command anywhere:
```bash
pip install -e .
```

---

## 🚀 Getting Started

Once installed, you need to set up the foundation before generating your first career plan.

**1. Initialize the Database**
Run this to create the local secure database to store your charts and plans (everything stays on your computer!):
```bash
bazi-career init
```

**2. Configure your AI Model**
Tell the system which AI you want to use (OpenAI, Anthropic, or DeepSeek) and paste your API key. Your key is stored securely and never uploaded.
```bash
bazi-career configure
```

---

## 💻 Full Command Reference

Here is a complete list of all the commands you can type into your terminal.

### Core Setup Commands
* `bazi-career init`
  * **What it does:** Sets up the necessary local folders and the SQLite database. Run this only once.
* `bazi-career configure`
  * **What it does:** An interactive prompt to select your AI provider (e.g., DeepSeek, OpenAI) and securely save your API key.
* `bazi-career doctor`
  * **What it does:** Checks your system to ensure everything (database, API keys, libraries) is configured correctly.

### Profile & Astrology Commands
* `bazi-career profile-create`
  * **What it does:** Creates a new user profile with your birth details (Year, Month, Day, Time, Location) and saves it to the database.
* `bazi-career chart`
  * **What it does:** Uses astronomical math to calculate your precise "Four Pillars" (BaZi) chart, adjusting for true solar time and the Southern Hemisphere if necessary.

### AI Workflow Commands
* `bazi-career validate --profile-id <id>`
  * **What it does:** The AI compares your calculated BaZi chart against your actual past career history to see how well they match, generating a "Confidence Score."
* `bazi-career recalibrate`
  * **What it does:** Fine-tunes the astrology rules for your specific profile if the validation score is too low.
* `bazi-career career-analyze`
  * **What it does:** Analyzes your raw skills and experience to build a standardized professional profile.
* `bazi-career plan-generate --profile-id <id>`
  * **What it does:** The magic command! The AI synthesizes your astrology chart and professional profile to output a detailed 1, 3, and 5-year career plan, complete with industry and role recommendations.

### Job Matching Commands (Phase 5+)
* `bazi-career jobs-discover`
  * **What it does:** Searches the web or parses provided URLs to find real-world job openings that fit your profile.
* `bazi-career jobs-rank`
  * **What it does:** Acts as a matchmaker. It scores the discovered jobs based on *both* your hard skills and your astrological luck cycles, ranking them from "Tier 1 (Perfect Match)" to "Tier 3 (Mismatch)".

---

## 💡 Example Workflow

If you want to go from zero to a full career plan, the flow looks like this:

```bash
# 1. Setup
bazi-career init
bazi-career configure

# 2. Input your data
bazi-career profile-create

# 3. Generate your chart
bazi-career chart

# 4. Generate the ultimate career plan
bazi-career plan-generate --profile-id my_profile_id
```

Enjoy exploring the intersection of ancient wisdom and modern AI!
