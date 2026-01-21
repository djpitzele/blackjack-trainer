<h1 align=center> Blackjack Trainer </h1>

A lightweight program to practice blackjack skills including perfect play and card counting. This program is focused more on learning than accurate simulation of blackjack (betting, hand outcomes, etc).

*Note: this program was created using AI assistance, namely from RooCode and Gemini*

# Quick Start
First, clone the repo to your local machine. There should not be any external dependencies.
```bash
git clone git@github.com:djpitzele/blackjack-trainer.git
cd blackjack-trainer
```
Then, run the main play script:
```bash
python src/gui_main.py
```
If you prefer to play in the CLI instead, there is an alternative script:
```bash
python src/main.py
```

# Future Plans
In the future, I would like to add the following features:
- A "for you" stream of hands that uses deep learning to figure out which hands you are worst at and serve you those
- (maybe) run my own Monte Carlo simulations to adjust perfect play depending on the count
