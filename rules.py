"""
Dice rolling and scoring rules for Tavern Dice.

The dice-rolling and scoring functions in this file
were independently written by Donglai Zheng.

ChatGPT Work later helped improve the English comments
and docstrings for the final submission.

See AI_DECLARATION.txt for details.
"""

import random


def roll_dice(amount=6):
    """Return a list of random dice values from 1 to 6.

    Raise ValueError unless amount is an integer from 1 to 6.
    """
    if type(amount) != int or amount < 1 or amount > 6:
        raise ValueError("The number of dice must be between 1 and 6.")

    dice = []
    for i in range(amount):
        dice.append(random.randint(1, 6))
    return dice


def has_scoring_dice(dice):
    """Return whether a roll contains at least one scoring selection.

    Every allowed straight includes a 1 or 5, so checking singles and
    matching groups also detects rolls that contain a straight.
    """
    if 1 in dice or 5 in dice:
        return True
    for number in range(1, 7):
        if dice.count(number) >= 3:
            return True
    return False


def score_same_number(number, count):
    """Score count dice showing the same number.

    Three 1s score 1000; other triples score number * 100. Each additional
    matching die doubles that score. Below three dice, only 1s and 5s
    score (100 and 50 each); other groups return 0.
    """
    if count >= 3:
        if number == 1:
            score = 1000
        else:
            score = number * 100
        for i in range(count - 3):
            score = score * 2
        return score

    if number == 1:
        return count * 100
    if number == 5:
        return count * 50
    return 0


def score_basic_groups(dice):
    """Add matching groups and single 1s or 5s, without using straights.

    Return 0 if any die is left in a non-scoring group, because every
    selected die must score. An empty list also returns 0.
    """
    total_score = 0
    for number in range(1, 7):
        count = dice.count(number)
        group_score = score_same_number(number, count)
        if count > 0 and group_score == 0:
            return 0
        total_score = total_score + group_score
    return total_score


def score_with_straight(dice, straight, straight_score):
    """Score one given straight plus any valid remaining groups.

    Remove the straight from a copy so the input list stays unchanged
    and no die scores twice. Return 0 if the straight is missing or
    any remaining dice cannot score.
    """
    remaining_dice = dice.copy()
    for number in straight:
        if number not in remaining_dice:
            return 0
        remaining_dice.remove(number)

    remaining_score = score_basic_groups(remaining_dice)
    if len(remaining_dice) > 0 and remaining_score == 0:
        return 0
    return straight_score + remaining_score


def score_selection(dice):
    """Return the highest valid score using every selected die exactly once.

    Compare basic groups with the 1-5, 2-6 and 1-6 straights. Return 0
    for an empty selection, more than six dice, invalid face values,
    or a selection that cannot be fully scored.
    """
    if len(dice) == 0 or len(dice) > 6:
        return 0
    for number in dice:
        if type(number) != int or number < 1 or number > 6:
            return 0

    basic_score = score_basic_groups(dice)
    low_score = score_with_straight(dice, [1, 2, 3, 4, 5], 500)
    high_score = score_with_straight(dice, [2, 3, 4, 5, 6], 750)
    full_score = score_with_straight(dice, [1, 2, 3, 4, 5, 6], 1500)
    return max(basic_score, low_score, high_score, full_score)
